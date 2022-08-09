FROM python:3.8 as base
# Base image to be reused
LABEL maintainer "team4devx"

RUN apt-get update
RUN mkdir /app
WORKDIR /app
COPY ./requirements.txt ./requirements.txt
RUN apt install libsystemd-dev build-essential libpython3-dev libdbus-1-dev libgirepository1.0-dev awscli  -y

RUN python -m pip install --upgrade pip
RUN pip install freezer
RUN pip install -r requirements.txt

EXPOSE 5000
COPY .aws /root/.aws
COPY . .

ARG PROFILE
ARG ACCESS_KEY
ARG SECRET_KEY
ARG REGION
WORKDIR /root/.aws
SHELL ["/bin/bash", "-c"]
RUN sed -i "s|ACCESS_KEY|$ACCESS_KEY|g" credentials
RUN sed -i "s|SECRET_KEY|$SECRET_KEY|g" credentials
RUN sed -i "s|REGION|$REGION|g" config
WORKDIR /app

RUN rm /etc/localtime
RUN ln -s /usr/share/zoneinfo/Asia/Seoul /etc/localtime

CMD ["gunicorn","--bind","0.0.0.0:5000","app:app"]
