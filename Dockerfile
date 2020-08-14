# pull official base image
FROM python:3-alpine

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=$PYTHONPATH:./mmvb_backend

#TODO: check if py3-numpy is needed
# Git for dependencies
RUN apk add --no-cache git py3-numpy

#TODO: Add no-cache-dir to pip install
# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app/requirements.txt
# Some magic to get mysql and numpy working
RUN apk add --no-cache mariadb-connector-c-dev ;\
    apk add --no-cache --virtual .build-deps \
        build-base \
        mariadb-dev ;\
    pip install -r requirements.txt --src /usr/src;\
    apk del .build-deps

# Add wait script to wait for mysql & redis
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.7.3/wait /wait
RUN chmod +x /wait

# copy entrypoint.sh
COPY ./entrypoint.sh /usr/src/app/entrypoint.sh

# copy project
COPY . /usr/src/app/