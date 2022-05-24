FROM node:10.0-alpine as build

WORKDIR /app
ADD . /app
RUN npm install &&\
    npm run build:staging

FROM nginx:1.15

COPY --from=build /app/dist/ /usr/share/nginx/html/
COPY --from=build /app/default.conf /etc/nginx/conf.d/default.conf
