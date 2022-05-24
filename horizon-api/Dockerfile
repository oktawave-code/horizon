FROM node:10.1.0-alpine

WORKDIR /app

ADD . /app

RUN npm install && \
    npm run build

EXPOSE 80

ENTRYPOINT [ "npm", "run", "start:simple" ]