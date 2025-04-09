# Message blog

## Prerequisites

Before you start, make sure you have:

- [pyenv](https://github.com/pyenv/pyenv) is installed
- [docker](https://www.docker.com/) is installed

## Start with docker
```bash
docker compose build --no-cache
docker compose up -d
make migrate
```


## Installation without docker

### 2. **Create a virtual environment**:
```bash
make setup
```

### 3. **Activate the virtual environment**:
```bash
source venv/bin/activate
```

## 3. Start PostgreSQL with Docker

```bash
docker compose up -d
```

## 4. Create migration

```bash
poetry run alembic revision --autogenerate -m 'Init'
```

## 5. Run migration

```bash
poetry run alembic upgrade head
```
