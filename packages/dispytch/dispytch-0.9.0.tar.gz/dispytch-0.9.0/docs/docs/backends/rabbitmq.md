# RabbitMQ Backend

Dispytch supports RabbitMQ as a backend for both emitting and consuming events.

It integrates cleanly with `aio-pika`, using AMQP 0.9.1 under the hood.

---

## Installation

```bash
pip install dispytch[rabbitmq]
````

This installs `aio-pika` and necessary dependencies.

---

## Producing Events (RabbitMQ Producer)

To emit events via RabbitMQ:

```python
import aio_pika
from dispytch_rabbitmq import RabbitMQProducer
from dispytch import EventEmitter

connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
channel = await connection.channel()

producer = RabbitMQProducer(channel)
emitter = EventEmitter(producer)
```

Now you can emit events like this:

```python
await emitter.emit(UserRegistered(...))
```

---

## Consuming Events (RabbitMQ Consumer)

To listen for events:

```python
from dispytch_rabbitmq import RabbitMQConsumer
from dispytch import EventListener

consumer = RabbitMQConsumer(channel, queue_name="user_events")
listener = EventListener(consumer)
```

Add your handlers and start listening:

```python
listener.add_handler_group(user_events)
await listener.listen()
```

---

## Notes on RabbitMQ Integration

* Each topic maps to a RabbitMQ queue.
* Messages are encoded as JSON.
* Acknowledgements are managed manually after successful handler execution.
* RabbitMQ does not support native partitions, so `__partition_by__` is ignored.
* Retry logic is handled by Dispytch — not RabbitMQ DLX or redelivery.

---

## Example Queue Declaration (Optional)

You can declare queues manually if needed:

```python
await channel.declare_queue("user_events", durable=True)
```

Dispytch will not auto-create queues.

