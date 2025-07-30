import asyncio
from typing import Annotated

import aio_pika
from pydantic import BaseModel

from dispytch import EventListener, Event, Dependency
from dispytch.consumers import RabbitMQConsumer


class MyEventBody(BaseModel):
    test: int


async def inner_dep(event: Event[MyEventBody]):
    print('inner_dep entered')
    yield event.body.test
    print('inner_dep exited')


async def outer_dep(test: Annotated[int, Dependency(inner_dep)],
                    test2: Annotated[int, Dependency(inner_dep)]):
    print('outer_dep entered')
    yield 5 + test + test2
    print('outer_dep exited')


async def main():
    connection = await aio_pika.connect('amqp://guest:guest@localhost:5672')
    channel = await connection.channel()
    queue = await channel.declare_queue('test_events')
    exchange = await channel.declare_exchange('test_events', aio_pika.ExchangeType.DIRECT)
    await queue.bind(exchange, routing_key='test_events')

    consumer = RabbitMQConsumer(queue)
    event_listener = EventListener(consumer)

    @event_listener.handler(topic='test_events', event='test_event')
    async def handle_event(event: Event[MyEventBody], test: Annotated[int, Dependency(outer_dep)]):
        print(event)
        print(test)
        await asyncio.sleep(2)

    await event_listener.listen()


if __name__ == '__main__':
    asyncio.run(main())
