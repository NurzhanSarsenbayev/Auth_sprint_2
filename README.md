
---

# 🎬 Online Cinema Platform (Sprint 7)

Микросервисный проект онлайн-кинотеатра:

* **Auth Service** — аутентификация, авторизация, социальные входы (OAuth), rate-limiting, трассировка.
* **Content Service** — API для фильмов, жанров, персон, поиск. Работает через Elasticsearch + Redis, проверяет JWT от Auth.
* **Admin Panel** — Django-админка для управления контентом. Интегрирована с Auth (SSO/JWT).

Все сервисы запускаются в `docker-compose`.

---
## Standalone Quickstart (Auth Service)

> Current focus: standalone Auth Service (Docker Compose).
> NOTE: at this stage the container entrypoint still applies migrations / seeds on boot.
> This will be removed in PR2 (explicit commands only).

### Requirements
- Docker + Docker Compose v2

### Run

```bash
cp auth_service/.env.auth.sample auth_service/.env.auth
make up
make health
```
Stop
```bash
make down
```
Ports
Auth API: http://localhost:8000/docs

Postgres: localhost:5433

Redis: localhost:6380

---
## 📂 Архитектура

```

[User] -> [Auth Service] -> issues JWT (RS256)
       -> [Content Service] -> проверяет JWT (JWKS кэш в Redis, fallback -> guest)
       -> [Admin Panel] -> работает через Auth (JWT/SSO), управляет БД фильмов
       
Infra: Postgres, Redis, Elasticsearch, Jaeger (трассировка)

```

* Все запросы между сервисами сопровождаются `x-request-id`.
* Трассировка (`OpenTelemetry`) отправляется в **Jaeger**.
* Если Auth недоступен → Content возвращает пользователя как `guest` (изящная деградация).

---

## 🚀 Запуск

### Требования

* Docker + Docker Compose
* Порты:

  * `8001` — Auth
  * `8002` — Content
  * `8003` — Admin Panel
  * `16686` — Jaeger UI

### Шаги

```bash
git clone https://github.com/<your_repo>/Auth_sprint_2.git
cd Auth_sprint_2
docker compose up --build
```

Через ~30 секунд сервисы будут доступны:

* Auth: [http://localhost:8001](http://localhost:8001)
* Content: [http://localhost:8002/api/v1/films](http://localhost:8002/api/v1/films)
* Admin: [http://localhost:8003/admin](http://localhost:8003/admin)
* Jaeger UI: [http://localhost:16686](http://localhost:16686)

---

## ⚙️ Переменные окружения

Для каждого сервиса есть свой `.env.example`.  
Чтобы запустить сервис, скопируйте пример и заполните при необходимости:

Называйте env файлы по схеме env.{service}: env.auth, env.admin и env.content

Тоже самое для тестов: env.test.{service}: env.test.auth, env.test.admin, env.test.content

---

## 🔐 OAuth вход

Поддерживаются:

* Google
* Yandex

Пример:

1. GET `/api/v1/oauth/google/login` → редирект в Google
2. После авторизации → колбэк `/api/v1/oauth/google/callback`
3. Пользователь создаётся в БД, выдаются JWT токены.
4. Можно отвязать: `DELETE /api/v1/oauth/google/unlink`

---

## 🧪 Тесты

Для каждого сервиса есть отдельный `docker-compose.test.yml`.
Запуск тестов (пример для Auth):

```bash
Content:

docker compose -f content_service/tests/docker-compose.test.content.yml up --build --abort-on-container-exit

Auth:

docker compose -f auth_service/tests/docker-compose.test.auth.yml up --build --abort-on-container-exit

Admin:

docker compose -f admin_panel/docker-compose.test.admin.yml up --build --abort-on-container-exit
```

---

## 📊 Трассировка

В Jaeger UI ([http://localhost:16686](http://localhost:16686)) можно отследить запросы:

* Auth Service (`auth_service`)
* Content Service (`content_service`)
* Admin Panel (`admin_service`)

Каждый запрос помечается `x-request-id`.

---

## ✨ Фичи проекта

* [x] JWT RS256 + JWKS
* [x] OAuth вход (Google, Yandex)
* [x] Rate limiting (Redis sliding window)
* [x] Partitioned login_history
* [x] Content API: фильмы, жанры, персоны + глобальный поиск
* [x] Admin Panel с inline-редактированием
* [x] Трассировка OpenTelemetry → Jaeger
* [x] Изящная деградация (guest при падении Auth)

---
