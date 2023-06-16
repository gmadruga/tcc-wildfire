init:
	docker run -d --name wildfire-analytics-local-db -p6379:6379 redis
	python3 api/main.py

start:
	docker start wildfire-analytics-local-db 
	python3 api/main.py

stop:
	docker stop wildfire-analytics-local-db

watch-db: 
	docker exec -it wildfire-analytics-local-db redis-cli

