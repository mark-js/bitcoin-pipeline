ARG python_version=3.12

FROM python:${python_version}-slim-bookworm

ARG hadoop_version=3
ARG jdk_version=17
ARG home=/home/user

RUN apt-get update && \
    apt-get install curl procps openjdk-${jdk_version}-jre-headless -y && \
    apt-get clean && \
    useradd -u 1000 -g 0 user && \
    mkdir -p /opt/data ${home} && \
    chown -R 1000:0 /opt/data ${home}

COPY requirements.txt .
RUN pip install -r requirements.txt

USER user
WORKDIR ${home}

RUN curl https://install.duckdb.org | sh

ENV PATH=${home}/.duckdb/cli/latest:${PATH} \
    PYTHONPATH=${home}