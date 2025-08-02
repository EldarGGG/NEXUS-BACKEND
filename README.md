# Nexus Platform Backend

Бэкенд часть платформы Nexus, построенная на Django REST API.

## 📚 Описание API

- `/api/docs/` - Swagger с описанием всех эндпоинтов
- `/api/schema/` - OpenAPI YAML схема
- `/api/v1/health/` - Эндпоинт проверки работоспособности для Railway
- `/health/` - Простой эндпоинт проверки статуса сервера

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

## 🚀 Деплой на Render

### Подготовка к деплою

1. Создайте аккаунт на [Render](https://render.com/)
2. Загрузите этот репозиторий на GitHub
3. В Render перейдите в раздел "Web Services" и нажмите "New Web Service"
4. Выберите ваш GitHub репозиторий
5. Добавьте PostgreSQL базу данных через раздел "PostgreSQL"

### Настройка веб-сервиса

При создании веб-сервиса укажите следующие настройки:

- **Name**: уникальное имя для вашего сервиса (например, nexus-backend)
- **Environment**: Python
- **Region**: выберите ближайший к вам регион
- **Branch**: main (или ваша основная ветка)
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `cd src && gunicorn core.wsgi:application`

### Настройка переменных окружения

Установите следующие переменные окружения в разделе "Environment Variables":

```
ENVIRONMENT=production
SECRET_KEY=<ваш-секретный-ключ>
DEBUG=False
DATABASE_URL=<автоматически-добавляется-render>
ALLOWED_HOSTS=<ваш-домен>.onrender.com
CORS_ALLOWED_ORIGINS=<url-вашего-фронтенда-на-vercel>
CSRF_TRUSTED_ORIGINS=<url-вашего-фронтенда-на-vercel>
PYTHON_VERSION=3.11.0
```

### Настройка автоматических миграций

Для автоматического запуска миграций добавьте в раздел "Advanced" следующий "Pre-deploy Command":

```
cd src && python manage.py migrate && python manage.py collectstatic --noinput
```

### Автоматический деплой

Render автоматически запустит:
1. Установку зависимостей из `requirements.txt`
2. Выполнение предварительных команд (Pre-deploy Command):
   - Миграции базы данных
   - Сбор статических файлов
3. Запуск приложения с помощью Gunicorn

## 📝 Связь с фронтендом

Фронтенд часть проекта находится в отдельном репозитории и должна быть развернута на Vercel.
После деплоя фронтенда не забудьте обновить переменные окружения `CORS_ALLOWED_ORIGINS` и `CSRF_TRUSTED_ORIGINS`.

## 🔧 Технический стек

- Django 5.0.2
- Django REST Framework
- Django REST Framework Simple JWT
- PostgreSQL (в production)
- SQLite (для разработки)
- Gunicorn
- WhiteNoise для статических файлов
- dj-database-url для конфигурации БД
- django-cors-headers для CORS

## 🐛 Устранение неполадок

### Проблемы с Health Check

Если health check не проходит:

1. **Проверьте логи сервера**
   ```bash
   docker logs <container-name>
   ```

2. **Протестируйте health endpoint вручную**
   ```bash
   curl http://localhost:8000/api/v1/health/
   curl http://localhost:8000/health/
   ```

3. **Проверьте зависимости**
   - Убедитесь, что все пакеты из `requirements.txt` установлены
   - Проверьте наличие `djangorestframework-simplejwt`

### Частые проблемы

1. **ModuleNotFoundError: No module named 'rest_framework_simplejwt'**
   - Решение: Установите недостающую зависимость: `pip install djangorestframework-simplejwt`

2. **Проблемы с подключением к базе данных**
   - Проверьте конфигурацию DATABASE_URL
   - Убедитесь, что база данных доступна

3. **Конфликты портов**
   - Измените переменную окружения `PORT`
   - Проверьте, не занят ли порт 8000

### Docker Health Check

Health check настроен для проверки:
- Доступности сервера
- Работоспособности Django приложения
- Подключения к базе данных (если доступна)

Конфигурация health check в `docker-compose.yml`:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health/"]
  interval: 10s
  timeout: 5s
  retries: 10
  start_period: 60s
```
