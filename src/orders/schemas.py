from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter

from .serializers import *

orders_list = {
    "tags": ["заказы"],
    "summary": "Получение заказов пользователя",
    "responses": {200: OpenApiResponse(response=OrderSerializer)}
}
orders_retrieve = {
    "tags": ["заказы"],
    "summary": "Получение конкретного заказа по ID",
    "responses": {200: OpenApiResponse(response=OrderSerializer)}
}
order_post = {
    "tags": ["заказы"],
    "summary": "Создание заказа на основе корзины",
    "parameters": [
        OpenApiParameter('comment', str, 'Комментарий к заказу'),
        OpenApiParameter('self_pickup_point', int, 'Точка самовывоза'),
    ],
}
protected_route = {
    "tags": ["тест защиты"],
    "summary": "проверка защищенного роута. токен нужно получить по api/v1/token/ и вводить с префиксом 'Token '",
    "parameters": [
        OpenApiParameter(
            location=OpenApiParameter.HEADER,
            name="Authorization",
            description='',
            type=str,

        )
    ],
}
orders_post_schema = {
    "post": extend_schema(**order_post)
}
orders_schemas = {
    "list": extend_schema(**orders_list),
    "retrieve": extend_schema(**orders_retrieve)
}

cart_get = {
    "tags": ["корзина"],
    "summary": "Получение корзины пользователя",
    "responses": {200: OpenApiResponse(response=CartSerializer)}
}
cart_post = {
    "tags": ["корзина"],
    "summary": "Добавление товара в корзину пользователя",
    "parameters": [
        OpenApiParameter('item', int, 'id of item'),
        OpenApiParameter('amount', int, 'deletes cart item if zero or negative amount provided'),
    ]
}
cart_delete = {
    "tags": ["корзина"],
    "summary": "Удаление товара из корзины пользователя",
    "parameters": [
        OpenApiParameter('item', int, 'id of item'),
    ]
}

cart_schemas = {
    "get": extend_schema(**cart_get),
    "post": extend_schema(**cart_post),
    "delete": extend_schema(**cart_delete),
}

stock_get = {
    "tags": ["остатки"],
    "summary": "Получение остатков по id",
    "responses": {200: OpenApiResponse(response=StockSerializer)}
}
stock_schemas = {
    "get": extend_schema(**stock_get),
}
stores_lits = {
    "tags": ["магазины"],
    "summary": "Получение всех **магазинов**",
    "responses": {200: OpenApiResponse(response=StoreSerializer)}
}
stores_retrieve = {
    "tags": ["магазины"],
    "summary": "Получение конкретного **магазина** по ID",
    "responses": {200: OpenApiResponse(response=StoreSerializer)}
}
stores_schemas = {
    "list": extend_schema(**stores_lits),
    "retrieve": extend_schema(**stores_retrieve)
}

items_list = {
    "tags": ["товары"],
    "summary": "Получение всех **товаров**",
    "responses": {200: OpenApiResponse(response=ItemSerializer)}
}
stores_retrieve = {
    "tags": ["товары"],
    "summary": "Получение конкретного **товара** по ID",
    "responses": {200: OpenApiResponse(response=ItemSerializer)}
}
items_schemas = {
    "list": extend_schema(**items_list),
    "retrieve": extend_schema(**stores_retrieve)
}

spp_list = {
    "tags": ["точки самовывоза"],
    "summary": "Получение всех **точек самовывоза**",
    "responses": {200: OpenApiResponse(response=SelfPickupPointSerializer)}
}
spp_retrieve = {
    "tags": ["точки самовывоза"],
    "summary": "Получение конкретной **точки самовывоза** по ID",
    "responses": {200: OpenApiResponse(response=SelfPickupPointSerializer)}
}

self_pickup_points_schemas = {
    "list": extend_schema(**spp_list),
    "retrieve": extend_schema(**spp_retrieve)
}
