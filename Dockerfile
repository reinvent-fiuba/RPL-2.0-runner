FROM python:3.7-alpine

WORKDIR /app

COPY requirements.txt ./

ENV PYTHONUNBUFFERED=1

RUN pip3 install -r requirements.txt

COPY . ./

ENTRYPOINT ["python3", "rabbitmq_receive.py"]