FROM python:3.12-slim-bookworm AS base

ARG spark_version=3.5.5
ARG hadoop_version=3
ARG jdk_version=17

ENV SPARK_HOME=/usr/local/bin/spark-${spark_version}-bin-hadoop3
ENV SPARK_MASTER_HOST=spark-master
ENV SPARK_MASTER_PORT=7077
ENV PYSPARK_PYTHON=python

RUN apt-get update -y && \
    apt-get install -y wget procps openjdk-${jdk_version}-jre-headless && \
    apt-get clean && \
    wget https://dlcdn.apache.org/spark/spark-${spark_version}/spark-${spark_version}-bin-hadoop3.tgz && \
    tar -xf spark-${spark_version}-bin-hadoop3.tgz -C /usr/local/bin/ && \
    rm spark-${spark_version}-bin-hadoop3.tgz && \
    useradd -m -u 1000 -g 0 user && \
    mkdir -p /opt/data && \
    chown -R 1000:0 ${SPARK_HOME} /opt/data

USER user
RUN mkdir ${SPARK_HOME}/logs

WORKDIR ${SPARK_HOME}


FROM base AS spark-master

ARG spark_master_web_ui=8080

EXPOSE ${spark_master_web_ui} ${SPARK_MASTER_PORT}
CMD bin/spark-class org.apache.spark.deploy.master.Master >> logs/spark-master.out


FROM base AS spark-worker

ARG spark_worker_web_ui=8081

EXPOSE ${spark_worker_web_ui}
CMD bin/spark-class org.apache.spark.deploy.worker.Worker spark://${SPARK_MASTER_HOST}:${SPARK_MASTER_PORT} >> logs/spark-worker.out