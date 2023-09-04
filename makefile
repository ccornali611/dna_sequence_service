install-req: 
	pip3 install -r requirements.txt
	pip3 install "typer[all]"

copy-config: 
	mkdir ./app/elastic_search/config
	cp ./copyit-config.ini ./app/elastic_search/config/config.ini

run-es:
	docker-compose up -d elasticsearch

run:
	docker-compose up -d elasticsearch
	docker-compose up -d dan_sequence_app

# running locally with elasticsearch docker
start-app:
	uvicorn app.main:app --host '0.0.0.0' --reload
