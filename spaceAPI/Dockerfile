FROM ubuntu:17.04

MAINTAINER Ansgar Schmidt <ansgar.schmidt@gmx.net>

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get upgrade -y && apt-get install -y python python-redis python-flask

RUN mkdir /spaceapi
WORKDIR   /spaceapi

ADD endpoint.json .
ADD frontend.py .
ADD config.ini .

EXPOSE 1341

CMD ["/usr/bin/python", "/spaceapi/frontend.py"]
