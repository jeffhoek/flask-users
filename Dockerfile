FROM python:3.11-buster as builder

WORKDIR /code

RUN pip install poetry

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

COPY pyproject.toml poetry.lock /code/

RUN poetry install --no-root && rm -rf $POETRY_CACHE_DIR

#
# Runtime image
#

FROM python:3.11-slim-buster as runtime

RUN apt-get update && \
    apt-get upgrade -y && \
    rm -rf /var/lib/apt/lists/*

ENV VIRTUAL_ENV=/code/.venv \
    PATH="/code/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY flask_users ./flask_users

USER 1001
ENV PYTHONPATH ./

ENTRYPOINT ["python3", "-m", "flask_users.app"]
