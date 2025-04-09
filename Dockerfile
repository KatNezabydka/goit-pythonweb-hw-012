FROM python:3.12-alpine3.20

ENV APP_HOME=/app
WORKDIR $APP_HOME

RUN apk add --no-cache gcc musl-dev python3-dev libffi-dev openssl-dev curl bash && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    export PATH="/root/.local/bin:$PATH" && \
    poetry --version

ENV PATH="/root/.local/bin:$PATH"

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root --no-interaction --no-ansi

COPY . .

EXPOSE 8000