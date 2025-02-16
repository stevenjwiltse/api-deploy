up:
	docker compose up -d; docker compose logs -f api;
down:
	docker compose down;
reup:
	docker compose down;
	docker compose up -d;
	docker compose logs -f api;