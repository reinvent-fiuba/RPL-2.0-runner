#!/usr/bin/env python
import pika
import functools
import receiver
import threading
from async_consumer import ReconnectingAsyncConsumer
from config import QUEUE_URL, QUEUE_ACTIVITIES_NAME, SYSTEMD

def ack_message(channel, delivery_tag):
    """Note that `channel` must be the same pika channel instance via which
    the message being ACKed was retrieved (AMQP protocol constraint).
    """
    if channel.is_open:
        channel.basic_ack(delivery_tag)
    else:
        # Channel is already closed, so we can't ACK this message;
        # log and/or do something that makes sense for your app in this case.
        pass


def do_work(connection, channel, delivery_tag, body):
    decoded = body.decode("utf-8")
    print(f" [x] Received {decoded}")

    subm, lang = decoded.split()

    try:
        receiver.ejecutar(subm, lang)
    except Exception as e:
        print("receiver tiro una exception!!!!", str(e))
        # TODO: ver como avisar que se proceso pero con error y que la quiero procesar devuelta
    finally:
        cb = functools.partial(ack_message, channel, delivery_tag)
        connection.add_callback_threadsafe(cb)


def on_message(channel, method, properties, body, args):
    (connection, threads) = args
    delivery_tag = method.delivery_tag
    t = threading.Thread(target=do_work, args=(connection, channel, delivery_tag, body))
    t.start()
    threads.append(t)

def start_consuming():
    connection = pika.BlockingConnection(pika.URLParameters(QUEUE_URL))
    channel = connection.channel()

    channel.queue_declare(
        queue=QUEUE_ACTIVITIES_NAME, durable=True, arguments={"x-message-ttl": 3600000}
    )

    channel.basic_qos(prefetch_count=1)

    threads = []

    on_message_callback = functools.partial(on_message, args=(connection, threads))
    channel.basic_consume(queue=QUEUE_ACTIVITIES_NAME, on_message_callback=on_message_callback)

    try:
        print(" [*] Waiting for messages. To exit press CTRL+C")
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()

    for thread in threads:
        thread.join()

    connection.close()

if __name__ == "__main__":

    if SYSTEMD:
        from systemd.daemon import notify

        print("Starting up ...")
        notify("READY=1")
        print("Startup complete")

    start_consuming()
