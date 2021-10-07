FROM python:3.8
LABEL maintainer="Sylvain Roy <sylvain.roy@m4x.org>"

ARG PHO_GOOGLE_MAP_API_KEY

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=1.0.5 \
    PHO_GOOGLE_MAP_API_KEY=$PHO_GOOGLE_MAP_API_KEY

RUN pip install "poetry==${POETRY_VERSION}"
ADD pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev --no-interaction

RUN mkdir /app
WORKDIR /app

ADD data ./data
ADD static ./static
ADD src ./src

CMD uvicorn --app-dir ./src server:app --host 0.0.0.0 --port 8000

EXPOSE 8000
