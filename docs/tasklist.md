# Sprint 7 — Project Tasks

---

## Auth Service
- [x] Добавить middleware `x-request-id`  
- [x] Настроить OpenTelemetry трассировку → Jaeger
- [x] Реализовать middleware rate limiting (Redis sliding window)
- [x] Добавить таблицу `social_accounts` (Alembic migration)
- [x] Реализовать OAuth:
  - [x] Google вход
  - [x] Yandex или VK вход
  - [x] Callback-роуты `/oauth/{provider}/callback`
- [x] Реализовать отвязку соц.аккаунта (`unlink`)
- [x!] Партиционировать таблицу:
  - [x] `login_history` по времени (месяц RANGE)
  - [ ] (или `users` по региону/другому критерию)

---

## Content Service
- [x] Добавить зависимость `auth_dep` для проверки JWT:
  - [x] JWKS из Auth, кэш в Redis
  - [x] Фон-обновитель JWKS
  - [x] Изящная деградация → `guest` если Auth/JWKS недоступен
- [x] Добавить middleware `x-request-id`
- [x] Подключить трассировку (OpenTelemetry → Jaeger)
- [x] (опционально) rate limiting

---

## Admin Panel
- [x] Поднять минимальный Django-проект
- [x] Создать app `movies/` с моделями `Filmwork`, `Genre`, `Person`
- [x] Настроить admin.py (inline-редактирование связей)
- [x] Интегрировать с Auth:
  - [x] Вход через JWT или SSO-прокси
  - [x] Проверка ролей (admin/editor)

---

## Интеграция и Тесты
- [x] Проверить сценарии деградации:
  - [x] Auth недоступен → пользователи становятся `guest`
  - [x] JWKS устарел → используем кэш
- [x] Написать интеграционные тесты:
  - [x] OAuth login + unlink
  - [x] Guest fallback
  - [x] Rate limit (429)
- [x] Проверить трассировку через Jaeger UI

---

## Документация
- [ ] Добавить `README.md` с:
  - [ ] Схемой архитектуры (auth ↔ content ↔ admin)
  - [ ] Инструкциями по запуску docker-compose
  - [ ] Примером .env
  - [ ] Примером проверки OAuth login
  - [ ] Как смотреть трассы в Jaeger