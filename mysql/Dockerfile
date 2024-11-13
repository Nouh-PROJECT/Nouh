FROM mysql:lts

ENV MYSQL_ROOT_PASSWORD=P@ss4RO

RUN rm /etc/my.cnf
COPY ./my.cnf /etc/my.cnf
COPY ./init.sql /docker-entrypoint-initdb.d/init.sql