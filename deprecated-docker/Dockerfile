FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /cras_digital

COPY requirements.txt /cras_digital/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /cras_digital/
