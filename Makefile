help:
	@sed -ne '/@sed/!s/## //p' $(MAKEFILE_LIST)

create:		## create docker volumes and network
	docker volume create bitcoin-pipeline-redpanda
	docker volume create bitcoin-pipeline-data
	docker volume create bitcoin-pipeline-airflow-postgres
	docker volume create bitcoin-pipeline-postgres
	docker network create bitcoin-pipeline-network
build:		## docker compose build
	docker compose -f docker-compose.yaml --profile app build
backend:	## docker compose up backend
	docker compose -f docker-compose.yaml up -d
run:		## docker compose up backend and app
	docker compose -f docker-compose.yaml up -d
	docker compose -f docker-compose.yaml up websocket-producer -d
	docker exec flink-jobmanager flink run -py bitcoin_pipeline/flink/run_postgres.py
	docker compose -f docker-compose.yaml up dash-app -d
down:		## docker compose down backend and app
	docker compose -f docker-compose.yaml --profile app down
remove:		## remove docker volumes and network. remove will delete stored data
	@echo -n "Are you sure you want to remove stored data? [y/N] " && read ans && [ $${ans:-N} = y ]
	docker volume remove bitcoin-pipeline-redpanda
	docker volume remove bitcoin-pipeline-data
	docker volume remove bitcoin-pipeline-airflow-postgres
	docker volume remove bitcoin-pipeline-postgres
	docker network remove bitcoin-pipeline-network
create-gcp:	## equivalent gcp deployment
	docker volume create bitcoin-pipeline-gcp-redpanda
	docker volume create bitcoin-pipeline-gcp-data
	docker volume create bitcoin-pipeline-gcp-airflow-postgres
	docker volume create bitcoin-pipeline-gcp-postgres
	docker network create bitcoin-pipeline-gcp-network
build-gcp:	## equivalent gcp deployment
	docker compose -f docker-compose-gcp.yaml --profile app build
backend-gcp:	## equivalent gcp deployment
	docker compose -f docker-compose-gcp.yaml up -d
run-gcp:	## equivalent gcp deployment
	docker compose -f docker-compose-gcp.yaml up -d
	docker compose -f docker-compose-gcp.yaml up websocket-producer -d
	docker exec flink-jobmanager flink run -py bitcoin_pipeline/flink/run_bigquery.py
	docker compose -f docker-compose-gcp.yaml up dash-app -d
down-gcp:	## equivalent gcp deployment
	docker compose -f docker-compose-gcp.yaml --profile app down
remove-gcp:	## equivalent gcp deployment
	docker volume remove bitcoin-pipeline-gcp-redpanda
	docker volume remove bitcoin-pipeline-gcp-data
	docker volume remove bitcoin-pipeline-gcp-airflow-postgres
	docker volume remove bitcoin-pipeline-gcp-postgres
	docker network remove bitcoin-pipeline-gcp-network
