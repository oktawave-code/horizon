FROM openjdk:8-jdk-alpine3.7 as build

WORKDIR /app
COPY . /app

RUN apk add sbt --update-cache --repository http://dl-3.alpinelinux.org/alpine/edge/testing/ --allow-untrusted &&\
    sbt universal:packageZipTarball &&\
    cd /app/target/universal &&\
    tar xvf *.tgz


FROM openjdk:8-jre-alpine3.7 AS runtime

WORKDIR /app
COPY --from=build /app/target/universal/play-java-starter-example-1.0-SNAPSHOT /app/

RUN apk update &&\
    apk add bash

ENV APPLICATION_PORT 80

ENTRYPOINT /bin/bash bin/play-java-starter-example -Dhttp.port=${APPLICATION_PORT}