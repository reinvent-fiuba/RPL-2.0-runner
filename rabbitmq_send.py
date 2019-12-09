#!/usr/bin/env python
import pika

import sys

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='hello')

channel.basic_publish(exchange='', routing_key='hello', body=sys.argv[1])
print(f" [x] Sent '{sys.argv[1]}'!")
connection.close()
