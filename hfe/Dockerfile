FROM maven:3.6.0-alpine as build

ARG MVN_PROFILE=hfejar

COPY . /usr/src/hfe

WORKDIR /usr/src/hfe

RUN mvn clean package -P $MVN_PROFILE

FROM openjdk:8-jdk-alpine

WORKDIR /app
COPY --from=build /usr/src/hfe/target/hfe-1.0-SNAPSHOT.jar .

ENTRYPOINT java -jar hfe-1.0-SNAPSHOT.jar
