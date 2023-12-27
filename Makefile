test:   
		docker build -t server -f Dockerfile-test .
		docker compose up -d
		pytest --disable-warnings || true 
		docker compose down

