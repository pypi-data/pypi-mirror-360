# EventEmitter

The **EventEmitter** is responsible for sending events to your chosen backend system, such as Kafka or RabbitMQ.

## Overview

- Wraps a low-level `Producer` interface.
- Accepts `EventBase` instances and serializes them into messages with metadata.
- Handles partition key extraction for partitioned backends like Kafka.
- Sends the message asynchronously.

## Usage

```python
from dispytch.emitter.event import EventBase
from dispytch.emitter.producer import Producer
from dispytch.emitter import EventEmitter

class UserRegistered(EventBase):
    __topic__ = "user_events"
    __event_type__ = "user_registered"
    __partition_by__ = "user.id"

    user: dict
    timestamp: int

producer = Producer(...)  # your Kafka or RabbitMQ producer setup
emitter = EventEmitter(producer)

await emitter.emit(UserRegistered(user={"id": "123"}, timestamp=1234567890))
