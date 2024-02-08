FROM python:3.8.12-buster

RUN apt-get update && \
    apt-get install -y git && \
    /usr/local/bin/python -m pip install --upgrade pip

ARG REPO_URL

WORKDIR /bot

RUN git clone ${REPO_URL} .

WORKDIR /bot/app

RUN pip3 install --no-cache-dir -r requirements.txt

CMD ["python", "./main_telebot.py"]
