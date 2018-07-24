FROM python:3.6

ENV PYTHONUNBUFFERED 1

RUN mkdir /www

WORKDIR /www

RUN apt-get update && apt-get -y --no-install-recommends install locales && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

RUN sed -i -e 's/# pt_BR.UTF-8 UTF-8/pt_BR.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen

RUN pip install pipenv

ADD . /www/

RUN pipenv lock

RUN pipenv sync
