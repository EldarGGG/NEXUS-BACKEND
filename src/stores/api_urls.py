from django.urls import path
from .api_views import StoreDetailAPIView, StoreItemsAPIView, StoreSubcategoriesAPIView
from .warehouse_api_views import WarehouseStockAPIView, WarehouseStatsAPIView
from .seller_api_views import SellerProductsAPIView, WarehousesAPIView, WarehouseDetailAPIView

urlpatterns = [
    path('stores/<int:store_id>/', StoreDetailAPIView.as_view(), name='store-detail'),
    path('stores/<int:store_id>/items/', StoreItemsAPIView.as_view(), name='store-items'),
    path('stores/<int:store_id>/subcategories/', StoreSubcategoriesAPIView.as_view(), name='store-subcategories'),
    
    # Warehouse management endpoints
    path('warehouse/stock/', WarehouseStockAPIView.as_view(), name='warehouse-stock'),
    path('warehouse/stats/', WarehouseStatsAPIView.as_view(), name='warehouse-stats'),
    
    # Seller endpoints
    path('seller/products/', SellerProductsAPIView.as_view(), name='seller-products'),
    path('warehouses/', WarehousesAPIView.as_view(), name='warehouses'),
    path('warehouses/<int:warehouse_id>/', WarehouseDetailAPIView.as_view(), name='warehouse-detail'),
]
