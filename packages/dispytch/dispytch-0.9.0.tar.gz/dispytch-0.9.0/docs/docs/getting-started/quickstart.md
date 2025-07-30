# Quickstart

Get up and running with Dispytch in under 5 minutes.

---

## 1. Define Your Event

Create an event by subclassing `EventBase`, specifying topic and event type metadata:

```python
from pydantic import BaseModel
from dispytch import EventBase

class UserRegistered(EventBase):
    __topic__ = "user_events"
    __event_type__ = "user_registered"

    user_id: str
    email: str
```

---

## 2. Register an Event Handler

Group handlers with `HandlerGroup` and register a function for your event:

```python
from dispytch import HandlerGroup

handlers = HandlerGroup()

@handlers.handler(topic="user_events", event="user_registered")
async def handle_user_registered(event):
    print(f"User {event.body.user_id} registered with email {event.body.email}")
```

---

## 3. Set Up the Emitter and Listener

Assuming you have a backend producer and consumer (e.g., Kafka):

```python
from dispytch.emitter import EventEmitter
from dispytch.listener import EventListener

producer = ...  # your Kafka or RabbitMQ producer instance
consumer = ...  # your Kafka or RabbitMQ consumer instance

emitter = EventEmitter(producer)
listener = EventListener(consumer)

listener.add_handler_group(handlers)
```

---

## 4. Emit and Listen for Events

```python
import asyncio

async def main():
    await emitter.emit(UserRegistered(user_id="123", email="user@example.com"))
    await listener.listen()

asyncio.run(main())
```

---

## That’s It!

You’ve defined an event, registered a handler, and started sending and receiving events asynchronously.

---

## Next Steps

* Configure your backend producer/consumer
* Explore retry policies and dependency injection
* Build real-world event-driven services
