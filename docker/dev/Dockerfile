ARG python_version=3.12

FROM python:${python_version}-slim-bookworm

ARG hadoop_version=3
ARG jdk_version=17

RUN apt-get update && \
    apt-get install curl procps openjdk-${jdk_version}-jre-headless -y && \
    apt-get clean && \
    useradd -u 1000 -g 0 user && \
    mkdir -p /opt/data /home/user && \
    chown -R 1000:0 /opt/data /home/user

COPY requirements.txt .
RUN pip install -r requirements.txt

USER user
WORKDIR /opt

RUN curl https://install.duckdb.org | sh

ENV PATH=/home/user/.duckdb/cli/latest:${PATH}

ENTRYPOINT [ "bash" ]