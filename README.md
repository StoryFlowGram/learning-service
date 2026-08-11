# Learning Service — SFG

> Spaced Repetition microservice. Manages user word flashcards, calculates optimal review intervals using the SM-2 algorithm, and dispatches word reminder events to RabbitMQ.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Running the Service](#running-the-service)
- [Environment Variables](#environment-variables)
- [API](#api)
- [Project Structure](#project-structure)

---

## Overview

Learning Service implements the core feature of the platform — **Spaced Repetition for vocabulary learning**:

- **Card Management**: Add words to personal learning queue (from books or manually)
- **SM-2 Algorithm**: Dynamically calculates the next review date and ease factor based on user performance (ratings 0–5)
- **Event Dispatching**: Publishes word reminder events to the `sfg.word-reminders` RabbitMQ queue when cards are due
- **Bot Integration**: Serves internal endpoints for `bot-service` to query due cards without JWT token checks

---

## Architecture

```
User Action (REST API)
        │
        ▼
┌───────────────────────┐
│    Learning Service   │
│  ┌──────────────────┐ │
│  │   Card Router    │ │
│  └────────┬─────────┘ │
│           │           │
│  ┌────────▼─────────┐ │
│  │   Use Cases      │ │  ← SM-2 Algorithm
│  └────────┬─────────┘ │
│           │           │
│  ┌────────▼─────────┐ │
│  │   PostgreSQL     │ │
│  └──────────────────┘ │
│           │ Events    │
│  ┌────────▼─────────┐ │
│  │   RabbitMQ       │ ├──▶ Bot Service
│  └──────────────────┘ │
└───────────────────────┘
```

---

## Technology Stack

| Package | Version | Role |
|--------|---------|------|
| `fastapi[all]` | ^0.120.0 | HTTP framework |
| `sqlalchemy` | ^2.0.44 | ORM |
| `asyncpg` | ^0.30.0 | Async PostgreSQL driver |
| `alembic` | ^1.17.1 | Database migrations |
| `aio-pika` | ^9.5.7 | RabbitMQ publisher |
| `pyjwt` | ^2.10.1 | JWT validation |
| `loguru` | ^0.7.3 | Logging |
| Python | ≥ 3.12 | Runtime |

---

## Running the Service

### Locally (Poetry)

```bash
cd Backend/learning-service
cp .env.example .env
poetry install
alembic upgrade head
uvicorn main:app --reload --port 8003
```

### Docker

```bash
docker build -t sfg-learning-service .
docker run -p 8003:8000 --env-file .env sfg-learning-service
```

---

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `POSTGRES_USER` | PostgreSQL username | `learning_user` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `learning_pass` |
| `POSTGRES_DB` | PostgreSQL database name | `learning_db` |
| `POSTGRES_HOST` | PostgreSQL host address | `learning-db` |
| `RABBITMQ_URL` | AMQP connection URI | `amqp://guest:guest@rabbitmq:5672/` |
| `INTERNAL_GATEWAY_TOKEN` | Token for internal service requests | `replace_me` |

---

## API

### `GET /health`

```json
{ "status": "ok", "service": "learning-service" }
```

### Cards — `/cards`

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/cards` | Create a new word card |
| `GET` | `/cards` | List user's flashcards |
| `GET` | `/cards/due` | Get cards due for review |
| `POST` | `/cards/{card_id}/review` | Submit review rating (0–5) |
| `DELETE` | `/cards/{card_id}` | Delete a flashcard |

---

## SM-2 Algorithm

The service uses **SuperMemo 2 (SM-2)** algorithm to calculate repetition intervals:

1. Each card stores `interval`, `repetitions`, and `ease_factor`.
2. After each review session, the user provides a score **0–5**.
3. Next interval calculation:
   - Score < 3: Reset (`interval = 1`, `repetitions = 0`)
   - Score ≥ 3: `interval *= ease_factor`, `ease_factor` updated dynamically

---

## Project Structure

```
learning-service/
├── main.py                   # FastAPI entrypoint
├── app/
│   ├── domain/               # Card entity & repository interfaces
│   ├── application/          # Use cases (Creation, Review, SM-2 math)
│   ├── infrastructure/       # SQLAlchemy models, repos, DI
│   └── presentation/         # Controllers & dependencies
├── alembic/                  # Database migrations
├── scripts/                  # Helper scripts
├── tests/                    # Unit & integration tests
├── Dockerfile
└── pyproject.toml
```
