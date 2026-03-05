FROM flink:1.17.2-scala_2.12-java11

RUN apt-get update -y && \
    apt-get install -y python3 python3-pip python3-dev maven && rm -rf /var/lib/apt/lists/* && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    apt-get clean

COPY requirements.txt pom.xml ./
RUN python -m pip install --upgrade pip && \
    pip install --upgrade google-api-python-client && \
    pip install -r requirements.txt --no-cache-dir && \
    mvn dependency:copy-dependencies -DoutputDirectory=/opt/flink/lib/ && \
    useradd -u 1000 -g 0 user && \
    chown -R 1000:0 /opt

USER user
    
WORKDIR /opt
ENV PYTHONPATH=/opt