FROM apache/airflow:2.10.4-python3.12

ARG jdk_version=17

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

USER root

RUN apt-get update -y && \
    apt-get install -y wget procps openjdk-${jdk_version}-jre-headless && \
    apt-get clean && \
    useradd -m -u 1000 -g 0 user && \
    mkdir /opt/data && \
    chown -R 1000:0 /opt/data

USER user

RUN 