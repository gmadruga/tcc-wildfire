init:
	docker run -d --name wildfire-analytics-local-db -p6379:6379 redis
	python3 api/main.py

start-api:
	docker start wildfire-analytics-local-db 
	python3 api/main.py

start-controler:
	python3 controller.py

stop:
	docker stop wildfire-analytics-local-db

watch-db: 
	docker exec -it wildfire-analytics-local-db redis-cli

start-exporter:
	python3 gcloud_scheduler.py