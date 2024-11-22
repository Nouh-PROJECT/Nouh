FROM mysql:lts

ENV MYSQL_ROOT_PASSWORD=P@ss4RO
ENV MYSQL_DATABASE=webapp
ENV MYSQL_USER=master
ENV MYSQL_PASSWORD=P@ss4MA

RUN rm /etc/my.cnf
COPY my.cnf /etc/my.cnf
COPY init.sql /docker-entrypoint-initdb.d/init.sql

EXPOSE 3306