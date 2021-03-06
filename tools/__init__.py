import os
import hashlib
import logging
import json

import requests
import pika
from geopy.geocoders import Nominatim
import geocoder


'''
Fix the id's for shema format
'''
def push_id(data, is_developer=True, is_complex=True, is_corp=True, is_flat=True):
  i_dev = 0
  for developer in data['developers']:
    if is_developer:
      data['developers'][i_dev]['id'] = i_dev
    i_comp = 0
    for complex in data['developers'][i_dev]['complexes']:
      if is_complex:
        data['developers'][i_dev]['complexes'][i_comp]['id'] = i_comp
      
      # prepare index for flat-layouts
      index = {}
      for fl in data['developers'][i_dev]['complexes'][i_comp]['flat-layouts']:
        index[fl['id']] = fl
      fin = {}
      for key in index.keys():
        id = hashlib.sha256(key.encode()).hexdigest()
        fl = index[key]
        fl['id'] = id
        fin[id] = fl
      newfl = []
      for fl in fin.keys():
        newfl.append(
          fin[fl]
        )
      data['developers'][i_dev]['complexes'][i_comp]['flat-layouts'] = newfl

      i_corp = 0
      for corp in data['developers'][i_dev]['complexes'][i_comp]['corps']:
        if is_corp:
          data['developers'][i_dev]['complexes'][i_comp]['corps'][i_corp]['id'] = i_corp
        i_flat = 0
        for flat in data['developers'][i_dev]['complexes'][i_comp]['corps'][i_corp]['flats']:
          flat['layout-id'] = index[flat['layout-id']]['id']
          flat = str(flat).encode()
          flat = hashlib.sha256(flat).hexdigest()
          if is_flat:
            data['developers'][i_dev]['complexes'][i_comp]['corps'][i_corp]['flats'][i_flat]['id'] = flat
          i_flat += 1
        i_corp += 1
      i_comp += 1
    i_dev += 1
  return data


'''
Sender can deliver messages to RabbitMQ
'''
def sender(data, **kwargs):
  config = {
    'uri': 'amqp://guest:guest@localhost/%2f',
    'exchange': 'exchange',
    'routing_key': '',
    'socket_timeout': 10,
    'content_type': 'application/json',
    'delivery_mode': 1,
    'headers': {}
  }
  for key in kwargs:
    config[key] = kwargs[key]
  config['params'] = pika.URLParameters(config['uri'])
  config['params'].socket_timeout = config['socket_timeout']
  config['connection'] = pika.BlockingConnection(config['params'])
  config['channel'] = config['connection'].channel()

  config['properties'] = pika.BasicProperties(
    delivery_mode = config['delivery_mode'],
    content_type = config['content_type'],
    headers = config['headers']
  )
  config['channel'].basic_publish(
    body=data,
    exchange=config['exchange'],
    routing_key=config['routing_key'],
    properties=config['properties']
  )
  config['connection'].close()







'''
Recive messages from RabbitMQ
'''
def reciver(**kwargs):
  config = {
    'uri': 'amqp://guest:guest@localhost/%2f',
    'exchange': 'exchange',
    'queue': 'queue',
    'routing_key': '',
    'socket_timeout': 10,
    'content_type': 'application/json',
    'delivery_mode': 1,
    'headers': {}
  }
  for key in kwargs:
    config[key] = kwargs[key]
  config['params'] = pika.URLParameters(config['uri'])
  config['params'].socket_timeout = config['socket_timeout']
  config['connection'] = pika.BlockingConnection(config['params'])
  config['channel'] = config['connection'].channel()

  config['properties'] = pika.BasicProperties(
    delivery_mode = config['delivery_mode'],
    content_type = config['content_type'],
    headers = config['headers']
  )

  for method_frame, properties, body in config['channel'].consume(
    config['queue']
  ):
    print(method_frame)
    print(properties)
    print(body.decode())
    config['channel'].basic_ack(method_frame.delivery_tag)
    break
  config['connection'].close()


def cmd_mqrecive():
  reciver(
    uri = os.environ['RABBITMQ_URI'],
    queue = os.environ['QUEUE']
  )







'''
Locator can help you detect lat&long for some string.
Please, ensure you have country name at start of address.
'''

class Locator(object):
  '''
  Ask yandex
  '''
  def get_yandex(self, address):
    data = geocoder.yandex(address).json
    return data['lat'], data['lng']
  '''
  Ask google
  '''
  def get_google(self, address):
    data = geocoder.google(address).geojson['features'][0]['properties']
    return data['lat'], data['lng']
  '''
  Ask OpenStreetMaps
  '''
  def get_other(self, address):
    data = Nominatim().geocode(address)
    return data.latitude, data.longitude
  '''
  Handle possible exceptions once
  '''
  def locate(self, address):
    try:
      return self.get_yandex(address)
    except:
      try:
        return self.get_google(address)
      except:
        return self.get_other(address)
  '''
  Handle possible exceptions 5 times
  '''
  def safe_locate(self, address):
    i = 0
    while i < 5:
      try:
        return self.locate(address)
        break
      except:
        pass
      i+=1



class TelegramNoti(object):
  tg_token = ''
  tg_base_url = 'https://api.telegram.org/bot'
  tg_url_messages = '/sendMessage'
  tg_url = ''
  data = ''
  message = ''
  tg_headers = {'Content-type': 'application/json'}
  parse_mode = 'Markdown'
  is_success = False

  def __init__(self, chat_id, token, message=None):
    logging.debug(
      'Created telegram object with args - chat_id: {}, message: {}, token: {}'.format(
        chat_id, message, token
      )
    )
    self.message = message
    self.chat_id = chat_id
    self.tg_token = token

  def prepare(self):
    logging.debug('Invoked prepare')
    self.tg_url = self.tg_base_url + self.tg_token + self.tg_url_messages
    logging.debug('Telegram api url: {}'.format(self.tg_url))
    self.data = {'chat_id': self.chat_id, 'text': self.message, 'parse_mode': self.parse_mode}
    logging.debug('Telegram service message: {}'.format(self.data))
    self.data = json.dumps(self.data)

  def request(self):
    logging.debug('Invoked request')
    try:
      result = requests.post(self.tg_url, data=self.data, headers=self.tg_headers)
      return self.humanise(result)
    except:
      return "Something wrong with networking"

  def humanise(self, result):
    logging.debug('Invoked humanise with status_code: {}'.format(result.status_code))
    if result.status_code == 200:
      self.is_success = True
      logging.info('Message delivered successefuly')
    elif result.status_code == 401:
      logging.error('Authorisation failed (check token)')
    else:
      logging.warning('Not-standart status-code')
      return result.content

  def send(self):
    logging.debug('Invoked send')
    self.prepare()
    answer = self.request()
    return answer

