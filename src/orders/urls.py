from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import *
from .mock_api_views import MockCartAPIView
from .dashboard_api_views import (
    DashboardStatsAPIView, OrdersListAPIView, ProductsListAPIView,
    StockRegistrationAPIView, WriteOffAPIView, InventoryCheckAPIView,
    ItemsListAPIView, StoragesListAPIView
)
from .real_api_views import (
    RealDashboardStatsAPIView, RealOrdersListAPIView, RealProductsListAPIView,
    TasksAPIView, ContractorsAPIView, AnalyticsAPIView
)
from .order_creation_api import (
    CreateOrderAPIView, UpdateOrderStatusAPIView, AddToCartAPIView, RealCartAPIView
)

router = DefaultRouter()
router.register(r"stores", StoreAPIView, basename='store')
router.register(r"users/orders", OrderAPIView, basename='order')


store_based_router = DefaultRouter()
store_based_router.register(r"items", ItemAPIView, basename='store')
store_based_router.register(r"self-pickup-points", SelfPickupPointAPIView, basename='self-pickup-point')

urlpatterns = [
    # Stock management
    path('stock/<int:item_id>/', StockAPIView.as_view()),
    
    # Order management - REAL APIs
    path('orders/create/', CreateOrderAPIView.as_view()),
    path('orders/<int:order_id>/status/', UpdateOrderStatusAPIView.as_view()),
    
    # Cart management - REAL APIs (main endpoint used by frontend)
    path('carts/', RealCartAPIView.as_view()),
    path('cart/add/', AddToCartAPIView.as_view()),
    path('carts/clear/', RealCartAPIView.as_view()),
    
    # Dashboard and seller APIs
    path('dashboard/stats/', DashboardStatsAPIView.as_view()),
    path('seller/orders/', OrdersListAPIView.as_view()),
    path('seller/products/', ProductsListAPIView.as_view()),
    
    # Inventory management APIs
    path('seller/inventory/registration/', StockRegistrationAPIView.as_view()),
    path('seller/inventory/write-offs/', WriteOffAPIView.as_view()),
    path('seller/inventory/checks/', InventoryCheckAPIView.as_view()),
    
    # Helper APIs for inventory forms
    path('seller/items/', ItemsListAPIView.as_view()),
    path('seller/storages/', StoragesListAPIView.as_view()),
    
    # Legacy/Mock APIs (for backward compatibility)
    # path('mock/carts/', MockCartAPIView.as_view()),  # Disabled to use real API
    path('mock/dashboard/stats/', DashboardStatsAPIView.as_view()),
    path('mock/seller/orders/', OrdersListAPIView.as_view()),
    path('mock/seller/products/', ProductsListAPIView.as_view()),
    
    # Router-based URLs
    path('', include(router.urls)),
    path('stores/<int:store_id>/', include(store_based_router.urls)),
    path('test/protected/', ProtectedView.as_view()),
]
