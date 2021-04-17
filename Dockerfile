FROM python:3.8
LABEL maintainer="Sylvain Roy <sylvain.roy@m4x.org>"

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=1.0.5

RUN pip install "poetry==${POETRY_VERSION}"

RUN mkdir /app
WORKDIR /app

ADD data ./data
ADD static ./static
ADD *.py ./

ADD pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction

CMD uvicorn server:app --host 0.0.0.0 --port 8000

EXPOSE 8000
