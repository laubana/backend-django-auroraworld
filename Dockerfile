FROM python:3.9.21-alpine

WORKDIR /app

COPY ./requirements.txt /app

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY ./ /app
