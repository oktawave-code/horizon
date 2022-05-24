FROM python:2.7-slim

RUN apt update && apt install -qq -y \
    netcat-openbsd \
    curl \
    iproute2

WORKDIR /monitor

ADD . /monitor

RUN pip install -r requirements.txt

CMD ["/bin/bash", "start.sh"]
