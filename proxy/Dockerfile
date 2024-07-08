# Description: Nginx Dockerfile
# User has less privileges than the root user
FROM nginxinc/nginx-unprivileged:1.21.1-alpine

COPY ./default.conf /etc/nginx/conf.d/default.conf
COPY ./uwsgi_params /etc/nginx/uwsgi_params
# Switch to root user to perform administrative tasks
USER root
RUN mkdir -p /usr/src/app/static
RUN chmod 755 /usr/src/app/static
# Switch back to the default unprivileged user
USER nginx