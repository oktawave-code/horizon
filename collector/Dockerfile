FROM golang:1.10.1-alpine3.7 as builder
WORKDIR /tmp/go/
ENV GOPATH /tmp/go
RUN mkdir /root/.ssh
ADD id_rsa /root/.ssh/id_rsa 
RUN chmod 600 /root/.ssh/id_rsa
ADD default_sshconfig /root/.ssh/config
ADD default_gitconfig /root/.gitconfig
RUN mkdir -p ${GOPATH}/src/collector
COPY *.go Gopkg.toml Gopkg.lock ./src/collector/
RUN apk --no-cache add git \
    build-base \
    openssh-client \
    && go get -d -u github.com/golang/dep \
    && cd $(go env GOPATH)/src/github.com/golang/dep \
    && DEP_LATEST=$(git describe --abbrev=0 --tags) \
    && git checkout $DEP_LATEST \
    && GOBIN=/usr/local/bin/ go install -ldflags="-X main.version=$DEP_LATEST" ./cmd/dep \
    && git checkout master \
    && cd ${GOPATH}/src/collector \
    && dep ensure \
    && CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -ldflags '-s' -o main *.go
RUN rm -vf /root/.ssh/id_rsa

FROM alpine:latest
WORKDIR /usr/local/bin/
RUN find / -name "main"
COPY --from=builder /tmp/go/src/collector/main .
EXPOSE 8080
CMD ["/usr/local/bin/main"]
