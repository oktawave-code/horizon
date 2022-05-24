FROM python:2.7-slim

WORKDIR /app

ADD . /app

RUN pip install -r requirements.txt

CMD ["python", "processor.py"]
