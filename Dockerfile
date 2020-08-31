# pull official base image
FROM python:3.8-alpine

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=$PYTHONPATH:./mmvb_backend:/usr/lib/python3.8/site-packages

# install dependencies
COPY ./requirements.txt /usr/src/app/requirements.txt

# Some magic to get mysql and numpy working
RUN apk add --no-cache mariadb-connector-c-dev py3-numpy ;\
    apk add --no-cache --virtual .build-deps \
        git \
        build-base \
        mariadb-dev ;\
    pip install -r requirements.txt --no-cache-dir --src /usr/src;\
    apk del .build-deps

# Add wait script to wait for mysql & redis
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.7.3/wait /wait
RUN chmod +x /wait

# copy entrypoint.sh
COPY ./entrypoint.sh /usr/src/app/entrypoint.sh

# copy project
COPY . /usr/src/app/