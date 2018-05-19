# Tools

Small python tools for every-day use


## Example amqp send

    sender(
      data = data,
      uri = os.environ['RABBITMQ_URI'],
      exchange = os.environ['EXCHANGE'],
      headers = {
        'ID': os.environ['ID']
      }
    )

## Example push_id use:

    data = push_id(data)
    
    data = push_id(
      data,
      is_developer=True,
      is_complex=True,
      is_corp=True,
      is_flat=False,
    )

## Locator

    tools.Locator().safe_locate('California')

## Telegram notify (bot)


#### Token:

    token = '000000000:AAAAAAAAAAAAAAAAAAAAA_BBBBBBBBBBBBB'

#### Fast-use:

    tools.TelegramNoti(chat_id=000000, token=token, message=1020).send()

#### Normal use:

    noti = tools.TelegramNoti(chat_id=000000, token=token)
    noti.message = 'Some msg'
    answer = noti.send

#### For integration tests:

    noti.tg_base_url = 'https://api.telegram.org/bot'
    noti.tg_url_messages = '/sendMessage'

#### Some options

    noti.tg_headers = {'Content-type': 'application/json'}
    noti.parse_mode = 'Markdown'

#### check:

    if not noti.is_success:
      raise Exception('Message not delivered')


