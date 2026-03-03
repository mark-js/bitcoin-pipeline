ARG python_version=3.12

FROM python:${python_version}-slim-bookworm

ARG home=/home/user

RUN useradd -u 1000 -g 0 user && \
    mkdir -p ${home} && \
    chown -R 1000:0 ${home}

COPY requirements.txt .
RUN pip install -r requirements.txt

USER user
WORKDIR ${home}
ENV PYTHONPATH=${home}