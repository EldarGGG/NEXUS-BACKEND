from django.urls import path
from .views import *

urlpatterns = [
    path('', root, name='home'),
    path('<int:back_store_id>/create/', create_store, name='create_store'),
    path('<int:store_id>/home/', home_store, name='home_store'),
    path('<int:store_id>/items/', store_items, name='store_items'),
    path('<int:store_id>/items/<int:item_id>/', item, name='item'),
    path('<int:store_id>/params/', store_params, name='store_params'),
    path('<int:store_id>/settings/', store_settings, name='store_settings'),
    path('<int:store_id>/integrations/', store_integrations, name='integrations'),
    path('<int:store_id>/moysklad/', moysklad, name='moysklad'),
]

htmx_patterns = [
    path('check-field/<str:field_name>', check_form_field, name='check-field'),
    path('<int:store_id>/pickup-points/create', create_pickup_point, name='create-pickup-point'),
    path('<int:store_id>/storages/create', create_storage, name='create-storage'),
    path('<int:store_id>/items/create', create_item, name='create-item'),
    path('<int:store_id>/moysklad/create', get_moysklad_token, name='get-moysklad-token'),
    path('<int:store_id>/items/<int:item_id>/images/create', create_item_image, name='create-item-image'),
    path('<int:store_id>/payment-methods/<int:payment_method_id>/create', create_connected_payment_method,
         name='create-connected-payment-method'),
    path('<int:store_id>/payment-methods/<int:payment_method_id>/delete', delete_connected_payment_method,
         name='delete-connected-payment-method'),
    path('pickup-points/<int:point_id>/delete', delete_pickup_point, name='delete-pickup-point'),
    path('items/<int:item_id>/delete', delete_item, name='delete-item'),
    path('storages/<int:storage_id>/delete', delete_storage, name='delete-storage'),
]

urlpatterns += htmx_patterns
