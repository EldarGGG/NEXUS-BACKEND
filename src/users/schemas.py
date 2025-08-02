from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter

# from .serializers import *


user_create = {
    "tags": ["авторизация"],
    "summary": "создание пользователя",
    "parameters": [
        OpenApiParameter('username', str, 'Юзернейм'),
        OpenApiParameter('email', str, 'Почта'),
        OpenApiParameter('password', str, 'Пароль'),
    ],
}

token_create = {
    "tags": ["авторизация"],
    "summary": "создание токена",
    "parameters": [
        OpenApiParameter('username', str, 'Юзернейм'),
        OpenApiParameter('password', str, 'Пароль'),
    ],
}

tg_token_create = {
    "tags": ["авторизация"],
    "summary": "создание токена через телеграм",
    "parameters": [
        OpenApiParameter('tgid', str, 'Telegram ID'),
    ],
}

