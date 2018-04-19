import os

import pika


def push_id(data):
  i_dev = 0
  for developer in data['developers']:
    data['developers'][i_dev]['id'] = i_dev
    i_comp = 0
    for complex in data['developers'][i_dev]['complexes']:
      data['developers'][i_dev]['complexes'][i_comp]['id'] = i_comp
      i_corp = 0
      for corp in data['developers'][i_dev]['complexes'][i_comp]['corps']:
        data['developers'][i_dev]['complexes'][i_comp]['corps'][i_corp]['id'] = i_corp
        i_flat = 0
        for flat in data['developers'][i_dev]['complexes'][i_comp]['corps'][i_corp]['flats']:
          data['developers'][i_dev]['complexes'][i_comp]['corps'][i_corp]['flats'][i_flat]['id'] = i_flat
          i_flat += 1
        i_corp += 1
      i_comp += 1
    i_dev += 1
  return data


def sender (data, **kwargs):
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
    body=body,
    exchange=config['exchange'],
    routing_key=config['routing_key'],
    properties=config['properties']
  )
  config['connection'].close()




