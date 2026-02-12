COMPOSE := docker compose
ENV_FILE := auth_service/.env.auth

.PHONY: help
help:
	@echo "Targets:"
	@echo "  make up        - start standalone auth stack"
	@echo "  make down      - stop stack"
	@echo "  make ps        - show containers"
	@echo "  make logs      - follow logs"
	@echo "  make logs-auth - auth service logs"
	@echo "  make health    - check API is up"
	@echo "  make init-env  - create auth_service/.env.auth from sample"

.PHONY: init-env
init-env:
	@test -f $(ENV_FILE) || cp auth_service/.env.auth.sample $(ENV_FILE)
	@echo "OK: $(ENV_FILE)"

.PHONY: up
up: init-env
	$(COMPOSE) up -d --build

.PHONY: down
down:
	$(COMPOSE) down -v

.PHONY: ps
ps:
	$(COMPOSE) ps

.PHONY: logs
logs:
	$(COMPOSE) logs -f --tail=200

.PHONY: logs-auth
logs-auth:
	$(COMPOSE) logs -f --tail=200 auth_service

.PHONY: health
health:
	@for i in 1 2 3 4 5 6 7 8 9 10; do \
		curl -fsS http://localhost:8000/docs >/dev/null && echo "OK: http://localhost:8000/docs" && exit 0; \
		sleep 1; \
	done; \
	echo "FAIL: API is not reachable"; exit 1

migrate:
	$(COMPOSE) exec auth_service alembic upgrade head

seed-roles:
	$(COMPOSE) exec auth_service python seed_roles.py

create-superuser:
	$(COMPOSE) exec auth_service python create_superuser.py

bootstrap: up migrate seed-roles health