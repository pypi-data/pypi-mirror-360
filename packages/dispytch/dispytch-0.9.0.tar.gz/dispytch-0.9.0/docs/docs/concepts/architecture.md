# Architecture Overview

Dispytch is designed as a modular, async-first event-handling framework for Python, built to simplify event-driven microservices.

## Core Components

- **EventBase**  
  The base class for all events. Events are typed Pydantic models with metadata (`__topic__`, `__event_type__`, etc.) that define where and how they get published.

- **EventEmitter**  
  Sends events to a backend (e.g., Kafka, RabbitMQ). Wraps a low-level producer and handles serialization, metadata, and partitioning.

- **EventListener**  
  Consumes events from the backend and dispatches them to registered handlers asynchronously. Manages task concurrency and retries.

- **HandlerGroup**  
  A registry to group and organize handlers by topic and event type, supporting decorators to simplify registration.

- **Dependency Injection (DI)**  
  Inspired by FastAPI, Dispytch allows you to annotate handler parameters for automatic dependency resolution, improving testability and modularity.

## Workflow

1. Define events by subclassing `EventBase`, specifying topic, event type, and payload.

2. Register handlers for events using decorators in `HandlerGroup` or directly on `EventListener`.

3. Use `EventEmitter` to send events to the backend.

4. The `EventListener` consumes incoming events and routes them to matching handlers, injecting dependencies.

5. Built-in retry logic manages transient failures without boilerplate.

## Extensibility

Dispytch is backend-agnostic and built to be composable. You can extend or override producers, consumers, and other core pieces without rewriting your business logic.

---

# Key Design Goals

- Async-first for scalability  
- Minimal boilerplate  
- Testability with pure async coroutines  
- Backend flexibility (Kafka, RabbitMQ, or custom)  
- Clear separation of concerns
