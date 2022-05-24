FROM golang:1.11.5-alpine3.8 as builder
WORKDIR /app
ENV GOPATH /tmp/go

RUN mkdir /root/.ssh
ADD id_rsa /root/.ssh/id_rsa
RUN chmod 600 /root/.ssh/id_rsa
ADD default_sshconfig /root/.ssh/config
ADD default_gitconfig /root/.gitconfig

COPY *.go go.mod go.sum ./

RUN apk --no-cache add git \
    build-base \
    openssh-client \
    && CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -ldflags '-s' -o proxy proxy.go \
    && rm -vf /root/.ssh/id_rsa

FROM alpine:latest
WORKDIR /usr/local/bin/
COPY --from=builder /app/proxy .
EXPOSE 8080
CMD ["/usr/local/bin/proxy"]
