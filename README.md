# Nexus Platform Backend

Бэкенд часть платформы Nexus, построенная на Django REST API.

## 📚 Описание API

- `/api/docs/` - Swagger с описанием всех эндпоинтов
- `/api/schema/` - OpenAPI YAML схема
- `/api/v1/health/` - Эндпоинт проверки работоспособности для Railway

## 🚀 Локальный запуск приложения (Windows)

### В первый раз

1. Открыть директорию проекта в терминале
2. `py -m venv venv` - создание виртуального окружения
3. `venv\Scripts\activate` - активация виртуального окружения
4. `pip install -r requirements.txt` - установка зависимостей
5. `cd src` - выбор рабочей директории
6. `py -m manage migrate` - запуск миграций, создание БД
7. `py -m manage createsuperuser` - регистрация суперюзера
8. `py -m manage runserver` - запуск приложения

### В последующие разы

1. Открыть директорию проекта в терминале
2. `venv\Scripts\activate` - активация виртуального окружения
3. `cd src` - выбор рабочей директории
4. `py -m manage runserver` - запуск приложения

## 🏗️ Структура проекта

- `core/` - Django core настройки и конфигурация
- `orders/` - Функциональность управления заказами
- `stores/` - Управление магазинами и товарами
- `users/` - Аутентификация и управление пользователями

## 🚀 Деплой на Railway

### Подготовка к деплою

1. Создайте аккаунт на [Railway](https://railway.app/)
2. Загрузите этот репозиторий на GitHub
3. В Railway создайте новый проект из GitHub репозитория
4. Добавьте PostgreSQL базу данных в проект

### Настройка переменных окружения

Установите следующие переменные окружения в Railway:

```
ENVIRONMENT=production
SECRET_KEY=<ваш-секретный-ключ>
DEBUG=False
DATABASE_URL=<автоматически-добавляется-railway>
ALLOWED_HOSTS=<ваш-домен-railway>.up.railway.app
CORS_ALLOWED_ORIGINS=<url-вашего-фронтенда-на-vercel>
CSRF_TRUSTED_ORIGINS=<url-вашего-фронтенда-на-vercel>
```

### Автоматический деплой

Railway автоматически запустит:
1. Установку зависимостей из `requirements.txt`
2. Запуск `entrypoint.sh`, который выполнит:
   - Миграции базы данных
   - Сбор статических файлов
   - Создание суперпользователя (если указаны переменные окружения)
   - Запуск Gunicorn

## 📝 Связь с фронтендом

Фронтенд часть проекта находится в отдельном репозитории и должна быть развернута на Vercel.
После деплоя фронтенда не забудьте обновить переменные окружения `CORS_ALLOWED_ORIGINS` и `CSRF_TRUSTED_ORIGINS`.

## 🔧 Технический стек

- Django 5.0.2
- Django REST Framework
- PostgreSQL (в production)
- SQLite (для разработки)
- Gunicorn
- WhiteNoise для статических файлов
- dj-database-url для конфигурации БД
- django-cors-headers для CORS
