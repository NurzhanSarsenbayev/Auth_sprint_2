COMPOSE := docker compose
ENV_FILE := auth_service/.env.auth
RUFF_PATHS := auth_service/src auth_service/*.py
MYPY_PATHS := \
  auth_service/src/core \
  auth_service/src/db \
  auth_service/src/utils/jwt.py \
  auth_service/src/utils/security.py

TEST_COMPOSE_FILE := auth_service/tests/docker-compose.test.auth.yml
TEST_COMPOSE := docker compose -f $(TEST_COMPOSE_FILE)

.PHONY: test test-up test-run test-logs test-down
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

test: test-up test-run test-down

test-up:
	$(TEST_COMPOSE) up -d --build test_postgres test_redis jaeger

test-run:
	$(TEST_COMPOSE) run --rm --no-deps tests bash -lc '\
		alembic -c alembic_test.ini upgrade head \
		&& SUPERUSER_PASSWORD=123 python create_superuser.py \
		&& pytest -q \
	'

test-logs:
	$(TEST_COMPOSE) logs -f --tail=200 tests

test-down:
	$(TEST_COMPOSE) down -v --remove-orphans

# --- Quality ---

lint:
	ruff check $(RUFF_PATHS)

fmt:
	ruff format $(RUFF_PATHS)

mypy:
	MYPYPATH=auth_service/src mypy $(MYPY_PATHS)

check: lint mypy

test: test-up test-run test-down

test-up:
	$(TEST_COMPOSE) up -d --build test_postgres test_redis jaeger

test-run:
	$(TEST_COMPOSE) run --rm --no-deps tests bash -lc '\
		alembic -c alembic_test.ini upgrade head \
		&& SUPERUSER_PASSWORD=123 python create_superuser.py \
		&& pytest -q \
	'

test-logs:
	$(TEST_COMPOSE) logs -f --tail=200 tests

test-down:
	$(TEST_COMPOSE) down -v --remove-orphans

# --- Quality ---
.PHONY: fmt lint typecheck quality

fmt:
	ruff format .

lint:
	ruff check auth_service/src auth_service/*.py

typecheck:
	MYPYPATH=auth_service/src mypy \
		auth_service/src/core \
		auth_service/src/db \
		auth_service/src/utils/jwt.py \
		auth_service/src/utils/security.py

quality: fmt lint typecheck

lint:
	ruff check $(RUFF_PATHS)

fmt:
	ruff format $(RUFF_PATHS)

mypy:
	MYPYPATH=auth_service/src mypy $(MYPY_PATHS)

check: lint mypy