FROM ghcr.io/dbt-labs/dbt-bigquery:1.9.0

RUN useradd -m -s /bin/bash -u 1000 user
USER user

WORKDIR /home/user/
COPY .dbt/ .dbt/
COPY bitcoin_analytics/ bitcoin_analytics/

WORKDIR /home/user/bitcoin_analytics/
ENTRYPOINT ["dbt"]
CMD ["run"]