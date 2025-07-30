import asyncio

import aio_pika

from dispytch import EventEmitter, EventBase
from dispytch.producers import RabbitMQProducer


class MyEvent(EventBase):
    __topic__ = 'test_events'
    __event_type__ = 'test_event'

    test: int


async def main():
    connection = await aio_pika.connect('amqp://guest:guest@localhost:5672')
    channel = await connection.channel()
    exchange = await channel.declare_exchange('test_events', aio_pika.ExchangeType.DIRECT)

    producer = RabbitMQProducer(exchange)
    event_emitter = EventEmitter(producer)
    await asyncio.sleep(0.5)

    for i in range(10):
        await event_emitter.emit(MyEvent(test=i))
        print(f'Event {i} sent')
        await asyncio.sleep(0.3)


if __name__ == '__main__':
    asyncio.run(main())
