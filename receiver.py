#!/usr/bin/env python
import os
from azure.servicebus import ServiceBusClient, ServiceBusMessage

CONNECTION_STR = os.environ['CONNECTION_STR']
QUEUE_NAME = os.environ['QUEUE_NAME']


servicebus_client = ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR, logging_enable=True)

with servicebus_client:
    receiver = servicebus_client.get_queue_receiver(queue_name=QUEUE_NAME, max_wait_time=600)
    with receiver:
        for msg in receiver:
            print("Received: " + str(msg))
            receiver.complete_message(msg)
