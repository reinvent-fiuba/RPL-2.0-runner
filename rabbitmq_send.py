#!/usr/bin/env python
import sys

import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='hello', durable=True)

channel.basic_publish(exchange='', routing_key='hello', body=sys.argv[1] + ' ' + sys.argv[2])
print(f" [x] Sent '{sys.argv[1]}' '{sys.argv[2]}'!")
connection.close()
