# Tools

Small python tools for every-day use


#### Example amqp send

    sender(
      data = data,
      uri = os.environ['RABBITMQ_URI'],
      exchange = os.environ['EXCHANGE'],
      headers = {
        'ID': os.environ['ID']
      }
    )

#### Example push_id use:

    data = push_id(data)

