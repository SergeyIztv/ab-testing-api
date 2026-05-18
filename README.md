# AB Testing API

Backend-сервис для управления A/B экспериментами, разработанный на Django.

---

## Стек

- Python 3
- Django
- Django REST Framework
- PostgreSQL
- Docker / Docker Compose
- OpenAPI (drf-spectacular)

---

## Описание

Сервис используется для проведения A/B тестирования в мобильных и веб-приложениях.

Клиент отправляет запрос с уникальным идентификатором устройства (`Device-Token`), после чего сервер возвращает список активных экспериментов и назначенных вариантов.

### Особенности

- Детерминированное распределение пользователей
- Один и тот же `Device-Token` всегда получает одинаковые варианты
- Новые эксперименты не отображаются старым устройствам
- Поддержка процентного распределения вариантов
- OpenAPI документация
- Контейнеризация через Docker

---

# API

## Получение экспериментов

```http
GET /api/v1/experiments/
```

### Headers

```http
Device-Token: 123e4567-e89b-12d3-a456-426614174000
```

### Пример ответа

```json
{
  "experiments": [
    {
      "key": "button_color",
      "value": "#FF0000"
    },
    {
      "key": "price",
      "value": "10"
    }
  ]
}
```

---

# Примеры экспериментов

## `button_color`

Проверка влияния цвета кнопки на конверсию.

### Варианты

| Значение | Распределение |
|---|---|
| `#FF0000` | 33.3% |
| `#00FF00` | 33.3% |
| `#0000FF` | 33.3% |

---

## `price`

Проверка влияния стоимости товара на прибыль.

### Варианты

| Значение | Распределение |
|---|---|
| `10` | 75% |
| `20` | 10% |
| `50` | 5% |
| `5` | 10% |

---

# Статистика

Административная страница со статистикой распределения пользователей:

```text
/admin/stats/
```

---

# OpenAPI документация

## Swagger UI

```text
/api/schema/swagger-ui/
```

## ReDoc

```text
/api/schema/redoc/
```

---

# Запуск через Docker

```bash
git clone git@github.com:SergeyIztov/ab-testing-api.git

cd ab-testing-api

docker compose up --build
```

---

# Локальный запуск

## 1. Клонировать репозиторий

```bash
git clone git@github.com:SergeyIztov/ab-testing-api.git

cd ab-testing-api
```

---

## 2. Создать виртуальное окружение

```bash
python -m venv venv
```

### Linux / macOS

```bash
source venv/bin/activate
```

### Windows

```powershell
venv\Scripts\activate
```

---

## 3. Установить зависимости

```bash
pip install -r requirements.txt
```

---

## 4. Применить миграции

```bash
python manage.py migrate
```

---

## 5. Запустить сервер

```bash
python manage.py runserver
```

---

# Тесты

```bash
pytest
```