FROM python:3.12-slim-bookworm

RUN useradd -m -s /bin/bash -u 1000 user

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /home/user/ingest/
COPY main.py .

USER user
ENTRYPOINT [ "python", "main.py" ]