#!/usr/bin/env python
import pika

import receiver

url = 'amqp://whtzemgn:ANQGgE-43kGy8It949iDpznyJduJeODM@buck.rmq.cloudamqp.com/whtzemgn'


def callback(ch, method, properties, body):
    decoded = body.decode("utf-8")
    print(f" [x] Received {decoded}")

    subm, lang = decoded.split()

    try:
        receiver.ejecutar(subm, lang)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print("receiver tiro una exception!!!!", str(e))
        ch.basic_ack(
            delivery_tag=method.delivery_tag)  # TODO: ver como avisar que se proceso pero con error y que la quiero procesar devuelta
        pass


def start_consuming():
    connection = pika.BlockingConnection(
        # pika.ConnectionParameters(host='localhost'))
        pika.URLParameters(url))
    channel = connection.channel()

    channel.queue_declare(queue='hello', durable=True, arguments={"x-message-ttl": 3600000})

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue='hello', on_message_callback=callback)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


if __name__ == '__main__':
    import systemd.daemon
    print('Starting up ...')
    systemd.daemon.notify('READY=1')
    print('Startup complete')

    start_consuming()
