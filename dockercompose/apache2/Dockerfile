FROM httpd:latest
RUN apt-get update && apt-get install -y curl
COPY ./httpd.conf /usr/local/apache2/conf/httpd.conf
COPY image.html /usr/local/apache2/htdocs/