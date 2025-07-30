# Kafka Backend

Dispytch has first-class support for Kafka as a message broker.

It supports:
- Emitting events to Kafka topics via a producer
- Consuming events from Kafka topics via a listener
- Manual partitioning via `__partition_by__`

---

## Installation

```bash
pip install dispytch[kafka]
````

This installs the required dependencies like `aiokafka`.

---

## Producing Events (KafkaProducer)

Use the built-in Kafka producer to emit events:

```python
from aiokafka import AIOKafkaProducer
from dispytch_kafka import KafkaProducer
from dispytch import EventEmitter

aioproducer = AIOKafkaProducer(bootstrap_servers="localhost:9092")
await aioproducer.start()

producer = KafkaProducer(aioproducer)
emitter = EventEmitter(producer)
```

Then emit as usual:

```python
await emitter.emit(UserRegistered(...))
```

---

## Consuming Events (KafkaConsumer)

Create a Kafka consumer and wire it into Dispytch:

```python
from aiokafka import AIOKafkaConsumer
from dispytch_kafka import KafkaConsumer
from dispytch import EventListener

aioconsumer = AIOKafkaConsumer(
    "user_events",
    bootstrap_servers="localhost:9092",
    group_id="my-service"
)
await aioconsumer.start()

consumer = KafkaConsumer(aioconsumer)
listener = EventListener(consumer)
```

---

## Partitioning Events

Kafka supports partitioned topics for scaling and ordering guarantees. Dispytch allows you to specify a partition key:

```python
class UserRegistered(EventBase):
    __topic__ = "user_events"
    __event_type__ = "user_registered"
    __partition_by__ = "user.id"  # supports dotted paths

    user: dict
    timestamp: int
```

Dispytch extracts the key at runtime and routes messages accordingly.

---

## Notes

* Dispytch does not manage topic creation or schema registration.
* Kafka retries and acks are handled at the Dispytch level, not via Kafka-specific settings.
* All messages are JSON-serialized using Pydantic under the hood.
