# Телеком Оператор — Учёт

Веб-приложение для учёта клиентов, заказов и начислений оператора связи.
Построено на Flask (Python) + PostgreSQL.

## Возможности

- **Клиенты** — база клиентов с инлайн-редактированием, статусами, тарифами
- **Заказы** — заказы из CRM с точками подключения, услугами, платежами
- **Заказы в стройке** — заказы в стадии организации с комментариями и контрольными датами
- **Фикс. начисления** — начисления по плану/факту с автогенерацией из эксплуатируемых заказов
- **Статистика** — отчёты по клиентам, кварталам, годам и статусам заказов

## Стек

- Python 3.10+
- Flask 3.0+
- PostgreSQL 12+
- psycopg2
- Tailwind CSS (CDN)

## Установка

### 1. Клонирование

```bash
git clone https://github.com/<ваш-username>/telecom-operator-accounting.git
cd telecom-operator-accounting/python_app
```

### 2. Виртуальное окружение

```bash
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate          # Windows
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка базы данных

Создайте базу данных PostgreSQL и примените схему:

```bash
createdb telecom
psql -d telecom -f schema.sql
```

### 5. Конфигурация

Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

Отредактируйте `.env`, указав ваши параметры подключения:

```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/telecom
SECRET_KEY=your-secret-key
```

### 6. Запуск

```bash
python app.py
```

Приложение будет доступно по адресу http://localhost:5000

## Структура проекта

```
python_app/
├── app.py              # Главный модуль Flask с маршрутами
├── config.py           # Чтение конфигурации из .env
├── db.py               # Доступ к PostgreSQL через psycopg2
├── constants.py        # Справочники статусов, тарифов
├── utils.py            # Форматирование, экспорт CSV
├── schema.sql          # Схема БД + тестовые данные
├── requirements.txt    # Зависимости
├── .env.example        # Пример конфигурации
├── static/
│   ├── app.js          # Inline-редактирование, поиск, модальные окна
│   └── app.css         # Стили
└── templates/
    ├── base.html       # Базовый шаблон
    ├── customers.html  # Страница клиентов
    ├── orders.html     # Страница заказов
    ├── construction.html # Заказы в стройке
    ├── charges.html    # Фикс. начисления
    └── statistics.html # Статистика
```

## Лицензия

Свободно для использования.
