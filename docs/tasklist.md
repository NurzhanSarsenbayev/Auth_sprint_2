# Sprint 7 — Project Tasks

---

## Auth Service
- [x] Добавить middleware `x-request-id`  
- [x] Настроить OpenTelemetry трассировку → Jaeger
- [x] Реализовать middleware rate limiting (Redis sliding window)
- [x] Добавить таблицу `social_accounts` (Alembic migration)
- [ ] Реализовать OAuth:
  - [ ] Google вход
  - [x] Yandex или VK вход
  - [x] Callback-роуты `/oauth/{provider}/callback`
- [x] Реализовать отвязку соц.аккаунта (`unlink`)
- [ ] Партиционировать таблицу:
  - [ ] `login_history` по времени (месяц RANGE)
  - [ ] (или `users` по региону/другому критерию)

---

## Content Service
- [ ] Добавить зависимость `auth_dep` для проверки JWT:
  - [ ] JWKS из Auth, кэш в Redis
  - [ ] Фон-обновитель JWKS
  - [ ] Изящная деградация → `guest` если Auth/JWKS недоступен
- [x] Добавить middleware `x-request-id`
- [x] Подключить трассировку (OpenTelemetry → Jaeger)
- [x] (опционально) rate limiting

---

## Admin Panel
- [ ] Поднять минимальный Django-проект
- [ ] Создать app `movies/` с моделями `Filmwork`, `Genre`, `Person`
- [ ] Настроить admin.py (inline-редактирование связей)
- [ ] Интегрировать с Auth:
  - [ ] Вход через JWT или SSO-прокси
  - [ ] Проверка ролей (admin/editor)

---

## Интеграция и Тесты
- [ ] Проверить сценарии деградации:
  - [ ] Auth недоступен → пользователи становятся `guest`
  - [ ] JWKS устарел → используем кэш
- [ ] Написать интеграционные тесты:
  - [ ] OAuth login + unlink
  - [ ] Guest fallback
  - [ ] Rate limit (429)
- [ ] Проверить трассировку через Jaeger UI

---

## Документация
- [ ] Добавить `README.md` с:
  - [ ] Схемой архитектуры (auth ↔ content ↔ admin)
  - [ ] Инструкциями по запуску docker-compose
  - [ ] Примером .env
  - [ ] Примером проверки OAuth login
  - [ ] Как смотреть трассы в Jaeger