# Installation

Install Dispytch from PyPI:

```bash
pip install dispytch
```

or using uv

```bash
uv add dispytch
```

---

## Backend Extras

Dispytch is backend-agnostic by default. To use specific backends, install the appropriate extras:

### Kafka

```bash
pip install dispytch[kafka]
```

or using uv

```bash
uv add dispytch[kafka]
```

Includes `aiokafka`.

### RabbitMQ

```bash
pip install dispytch[rabbitmq]
```

or using uv

```bash
uv add dispytch[rabbitmq]
```

Includes `aio-pika`.

---