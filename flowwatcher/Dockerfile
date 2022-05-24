FROM python:2.7-slim

RUN apt update && apt install -qq -y \
    netcat-openbsd \
    curl \
    iproute2

WORKDIR /controller

ADD . /controller

RUN pip install -r requirements.txt

CMD ["/bin/bash", "start.sh"]
