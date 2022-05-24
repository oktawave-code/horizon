FROM python:3.7.0-alpine3.8

WORKDIR /app

ADD . /app

RUN pip install -r requirements.txt

CMD ["python", "processor.py"]
