#!/usr/bin/env python
import os
import json
import asyncio
from azure.servicebus import ServiceBusClient
from faster_than_light import run_module, load_inventory
import multiprocessing as mp

CONNECTION_STR = os.environ['CONNECTION_STR']
QUEUE_NAME = os.environ['QUEUE_NAME']
TOKEN = os.environ['TOKEN']


def source(queue):

    servicebus_client = ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR,
                                                                logging_enable=True)

    with servicebus_client:
        receiver = servicebus_client.get_queue_receiver(queue_name=QUEUE_NAME, max_wait_time=600)
        with receiver:
            for msg in receiver:
                data = json.loads(str(msg))
                print(data)
                queue.put(data)
                receiver.complete_message(msg)


def run_rules(queue):

    while True:
        data = queue.get()
        print(data)
        asyncio.run(run_module(load_inventory('inventory.yml'),
                               ['modules'],
                               'slack',
                               modules=['slack'],
                               module_args=dict(token=TOKEN, msg=str(data))))


async def main():

    queue = mp.Queue()

    tasks = []

    tasks.append(mp.Process(target=source, args=(queue,)))
    tasks.append(mp.Process(target=run_rules, args=(queue,)))

    for task in tasks:
        task.start()

    for task in tasks:
        task.join()


if __name__ == "__main__":
    asyncio.run(main())
