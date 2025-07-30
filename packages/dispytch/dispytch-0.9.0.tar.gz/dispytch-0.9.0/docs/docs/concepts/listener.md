# EventListener

The **EventListener** orchestrates consuming events from your backend and dispatching them to the right handlers.

---

## Overview

- Consumes events asynchronously from a `Consumer` interface.
- Matches events by topic and event type to registered handlers.
- Supports concurrent handler execution with asyncio tasks.
- Provides retry logic and error logging on failures.
- Supports handler registration via decorators or by importing `HandlerGroup`s.

---

## Core Responsibilities

1. **Listening**  
   Uses `async for` to listen for incoming events from the backend.

2. **Dispatching**  
   Finds all handlers matching the event’s topic and type.

3. **Dependency Injection**  
   Injects dependencies into handlers, allowing clean, decoupled code.

4. **Task Management**  
   Creates asyncio tasks for each handler call and manages their lifecycle.

5. **Acknowledgement**  
   Calls the consumer’s ack method on successful handling.

---

## Example Usage

```python
listener = EventListener(consumer)  # consumer is your Kafka/RabbitMQ consumer instance

@listener.handler(topic="user_events", event="user_registered")
async def handle_user_registered(event):
    print(f"Received user_registered: {event.body}")

await listener.listen()
```

---

## Registering Handler Groups

You can register multiple handlers grouped logically:

```python
listener.add_handler_group(user_events)
```

Where `user_events` is an instance of `HandlerGroup` containing handlers registered via decorators.

---

## Notes

* If no handler matches an event, an info log is emitted.
* Handler failures log exceptions but do not crash the listener.
* Retries and retry intervals can be configured per handler.

