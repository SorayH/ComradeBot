FROM python:3.8.12-buster

RUN /usr/local/bin/python -m pip install --upgrade pip

WORKDIR /bot

COPY . .
RUN pip3 install --no-cache-dir -r requirements.txt

CMD ["python", "./main.py"]