FROM python:3.8
LABEL maintainer="Sylvain Roy <sylvain.roy@m4x.org>"

ENV PIP_DISABLE_PIP_VERSION_CHECK=on

RUN mkdir /var/app
WORKDIR /var/app

ADD requirements.txt /var/app/
RUN pip install -r requirements.txt

ADD *.py /var/app/
ADD static /var/app/static
ADD data /var/app/data

CMD uvicorn server:app --host 0.0.0.0 --port 8000

EXPOSE 8000
