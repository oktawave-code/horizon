FROM python:2.7-slim

RUN apt update && apt install -qq -y \
    netcat-openbsd \
    curl \
    iproute2

ADD ["main.py","requirements.txt","/usr/src/app/"]

WORKDIR /usr/src/app/

RUN pip install -r requirements.txt

EXPOSE 5000
ENTRYPOINT ["/usr/local/bin/gunicorn"]

CMD ["-w","1","-b","0.0.0.0:5000","--threads","1","main:app","--access-logfile","/dev/stdout","--error-logfile","/dev/stdout"]
