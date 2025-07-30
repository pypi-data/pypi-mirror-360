# Dependency Injection (DI)

Dispytch incorporates a **FastAPI-inspired Dependency Injection system** to simplify handler dependencies and improve testability.

---

## Why DI?

- Decouples handler business logic from infrastructure concerns.
- Enables clean, declarative handler signatures.
- Automatically resolves and injects dependencies at runtime.
- Supports async and sync dependencies.

---

## How It Works

Handlers declare dependencies using Python’s type annotations combined with Dispytch’s `Dependency` wrapper.

Example:

```python
from typing import Annotated
from dispytch import Dependency

async def get_user_service():
    # Setup or retrieve a service instance
    return UserService()

@handler_group.handler(topic="user_events", event="user_registered")
async def handle_user_registered(
    event: Event[UserRegisteredEvent],
    user_service: Annotated[UserService, Dependency(get_user_service)]
):
    await user_service.do_something(event.body.user)
```

At runtime, Dispytch:

1. Inspects the handler’s parameters.
2. Detects `Dependency` annotations.
3. Resolves and injects the requested dependencies before invoking the handler.

---

## Features

* Supports async/sync factory functions for dependencies.
* Automatically manages dependency lifecycles.
* Allows passing context, such as the current event, to dependency resolvers.
* Easily testable by overriding dependencies in tests.

---

## Advanced Usage

You can create reusable dependencies for common resources (DB sessions, caches, config objects), keeping your handlers clean and focused.

---

## Notes

* DI is optional but recommended for complex services.
* Keep dependency trees shallow to avoid performance issues.
* Currently designed to work seamlessly within Dispytch’s event handling lifecycle.

