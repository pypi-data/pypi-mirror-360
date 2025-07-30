# HandlerGroup

A **HandlerGroup** is a container that organizes and registers event handlers by topic and event type.

---

## Purpose

- Helps you group related handlers logically.
- Simplifies handler registration with decorators.
- Supports default topic and event values to reduce repetition.
- Stores metadata like retry settings per handler.

---

## Usage

Create a handler group and register handlers using the `.handler()` decorator:

```python
from dispytch import HandlerGroup

user_events = HandlerGroup(default_topic="user_events")

@user_events.handler(event="user_registered", retries=3, retry_interval=2.0)
async def handle_user_registered(event):
    print(f"User registered: {event.body}")
```

---

## Handler Registration

The `.handler()` decorator accepts:

| Parameter        | Description                                         | Default                               |
| ---------------- | --------------------------------------------------- | ------------------------------------- |
| `topic`          | Event topic to listen to (overrides default\_topic) | `default_topic` if set, else required |
| `event`          | Event type to handle (overrides default\_event)     | `default_event` if set, else required |
| `retries`        | Number of retry attempts on failure                 | `0`                                   |
| `retry_on`       | Exception type to trigger retries (any if not set)  | `Exception`                           |
| `retry_interval` | Delay between retries in seconds                    | `1.25`                                |

---

## Registering with an EventListener

To use a `HandlerGroup`, register it with an `EventListener`:

```python
listener.add_handler_group(user_events)
```

This imports all handlers in the group into the listener’s dispatching system.

---

## Error Handling & Validation

* Raises `TypeError` if topic or event type is not specified either in the decorator or default group.
* Supports flexible retry strategies for robust event processing.

