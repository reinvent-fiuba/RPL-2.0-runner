#!/usr/bin/env python
import sys
import time
import random

import pika
from config import QUEUE_URL

connection = pika.BlockingConnection(pika.URLParameters(QUEUE_URL))
channel = connection.channel()

channel.queue_declare(queue="hello", durable=True, arguments={"x-message-ttl": 3600000})

for i in range(100):
    channel.basic_publish(
        exchange="", routing_key="hello", body=sys.argv[1] + " " + sys.argv[2]
    )
    print(f" [x] Sent '{sys.argv[1]}' '{sys.argv[2]}'!")
    s = random.randint(0, 3)
    print(f"sleeping for {s} seconds")
    time.sleep(s)
connection.close()
