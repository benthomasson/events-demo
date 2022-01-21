#!/usr/bin/env python
import os
import json
from azure.servicebus import ServiceBusClient
from pprint import pprint

CONNECTION_STR = os.environ['CONNECTION_STR']
QUEUE_NAME = os.environ['QUEUE_NAME']


servicebus_client = ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR,
                                                            logging_enable=True)

with servicebus_client:
    receiver = servicebus_client.get_queue_receiver(queue_name=QUEUE_NAME, max_wait_time=600)
    with receiver:
        for msg in receiver:
            data = json.loads(str(msg))
            print('='*80)
            pprint(data)
            receiver.complete_message(msg)
