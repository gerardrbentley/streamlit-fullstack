FROM nginx:1.21

WORKDIR /usr/src/nginx
COPY . /usr/src/nginx

COPY /conf/project.conf /etc/nginx/conf.d/
RUN rm /etc/nginx/conf.d/default.conf