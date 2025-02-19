# Install Poetry and create venv in the builder step,
# then copy the venv to the runtime image, so that the runtime image is as small as possible.
FROM --platform=linux/amd64 python:3.10.14-bookworm AS builder

RUN pip install poetry==1.8.2

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --no-root

FROM --platform=linux/amd64 python:3.10.14-bookworm AS runtime

RUN apt-get update && apt-get install -y postgresql

RUN useradd -m appuser

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY pyproject.toml poetry.lock ./
COPY labs_api labs_api
COPY tests tests

ENV PYTHONPATH=/app

CMD ["bash", "-c", "python labs_api/main.py"]
