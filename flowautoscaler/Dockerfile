FROM python:2.7-slim

RUN apt update && apt install -qq -y \
    netcat-openbsd \
    curl \
    iproute2

WORKDIR /autoscaler

ADD . /autoscaler

RUN pip install -r requirements.txt

CMD ["/bin/bash", "start.sh"]
