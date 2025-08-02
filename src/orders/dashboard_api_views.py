from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Sum

from stores.models import Store, Item, Group, Uom, Enter, WriteOff, InventoryCheck, InventoryCheckItem, Stock, Storage
from orders.models import Order, Task, Counterparty
from decimal import Decimal


class DashboardStatsAPIView(APIView):
    """
    Get dashboard statistics for seller
    GET /api/v1/dashboard/stats/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # Get user's store (middleware ensures this exists)
            user_store = getattr(request, 'user_store', None)
            if not user_store:
                try:
                    user_store = Store.objects.get(owner=request.user)
                except Store.DoesNotExist:
                    return Response(
                        {"detail": "У пользователя нет магазина"}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            # Calculate real statistics for user's store
            today = timezone.now().date()
            
            # Orders statistics
            total_orders = Order.objects.filter(store=user_store).count()
            pending_orders = Order.objects.filter(store=user_store, status='pending').count()
            completed_orders = Order.objects.filter(store=user_store, status='delivered').count()
            today_orders = Order.objects.filter(store=user_store, created_at__date=today).count()
            
            # Revenue statistics
            total_revenue = Order.objects.filter(store=user_store).aggregate(
                total=Sum('total_price')
            )['total'] or Decimal('0.00')
            
            today_revenue = Order.objects.filter(
                store=user_store, 
                created_at__date=today
            ).aggregate(total=Sum('total_price'))['total'] or Decimal('0.00')
            
            # Products statistics
            total_products = Item.objects.filter(store=user_store).count()
            
            # Recent activity
            recent_orders = Order.objects.filter(store=user_store).order_by('-created_at')[:3]
            recent_activity = []
            
            for order in recent_orders:
                recent_activity.append({
                    "type": "order",
                    "message": f"Заказ #{order.order_number} от {order.user.first_name} {order.user.last_name}",
                    "timestamp": order.created_at.isoformat()
                })
            
            # Top products (mock for now - can be implemented with OrderItem aggregation)
            top_products = [
                {"name": "Популярный товар 1", "sales": 0},
                {"name": "Популярный товар 2", "sales": 0},
                {"name": "Популярный товар 3", "sales": 0}
            ]
            
            stats = {
                "totalOrders": total_orders,
                "totalProducts": total_products,
                "totalRevenue": float(total_revenue),
                "pendingOrders": pending_orders,
                "completedOrders": completed_orders,
                "todayOrders": today_orders,
                "todayRevenue": float(today_revenue),
                "topProducts": top_products,
                "recentActivity": recent_activity,
                "storeInfo": {
                    "id": user_store.id,
                    "name": user_store.name,
                    "description": user_store.description
                }
            }
            return Response(stats)
        except Exception as e:
            return Response(
                {"detail": f"Error: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class OrdersListAPIView(APIView):
    """
    Get orders list for seller
    GET /api/v1/orders/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # Get user's store
            user_store = getattr(request, 'user_store', None)
            if not user_store:
                try:
                    user_store = Store.objects.get(owner=request.user)
                except Store.DoesNotExist:
                    return Response(
                        {"detail": "У пользователя нет магазина"}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            # Get orders for user's store only
            orders_queryset = Order.objects.filter(store=user_store).order_by('-created_at')
            
            orders = []
            for order in orders_queryset:
                order_items = []
                for item in order.items.all():
                    order_items.append({
                        "name": item.item.name,
                        "quantity": item.amount,
                        "price": float(item.price_per_item)
                    })
                
                orders.append({
                    "id": order.id,
                    "order_number": order.order_number,
                    "customer": f"{order.user.first_name} {order.user.last_name}",
                    "customer_email": order.user.email,
                    "total": float(order.total_price),
                    "status": order.status,
                    "created_at": order.created_at.isoformat(),
                    "delivery_address": order.delivery_address,
                    "comment": order.comment,
                    "items": order_items
                })
            
            return Response(orders)
        except Exception as e:
            return Response(
                {"detail": f"Error: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProductsListAPIView(APIView):
    """
    Get products list for seller and create new products
    GET /api/v1/seller/products/ - List products
    POST /api/v1/seller/products/ - Create product
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # Get user's store
            user_store = getattr(request, 'user_store', None)
            if not user_store:
                try:
                    user_store = Store.objects.get(owner=request.user)
                except Store.DoesNotExist:
                    return Response(
                        {"detail": "У пользователя нет магазина"}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            # Get products for user's store only
            products_queryset = Item.objects.filter(store=user_store).order_by('-created_at')
            
            products = []
            for product in products_queryset:
                # Calculate total stock from all storages
                total_stock = 0
                try:
                    stocks = Stock.objects.filter(item=product)
                    total_stock = sum(stock.amount for stock in stocks)
                except:
                    total_stock = 0
                
                products.append({
                    "id": product.id,
                    "name": product.name,
                    "price": float(product.default_price),
                    "stock": total_stock,
                    "category": product.group.name if product.group else "Нет категории",
                    "status": "active" if product.status else "inactive",
                    "created_at": product.created_at.isoformat(),
                    "image": product.preview.url if product.preview else None,
                    "uom": product.uom.name if product.uom else "шт."
                })
            
            return Response(products)
        except Exception as e:
            return Response(
                {"detail": f"Error: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """Create new product for user's store"""
        try:
            # Get user's store
            user_store = getattr(request, 'user_store', None)
            if not user_store:
                try:
                    user_store = Store.objects.get(owner=request.user)
                except Store.DoesNotExist:
                    return Response(
                        {"detail": "У пользователя нет магазина"}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            data = request.data
            
            # Validate required fields
            required_fields = ['name', 'price']
            missing_fields = [field for field in required_fields if not data.get(field)]
            if missing_fields:
                return Response(
                    {"detail": f"Missing required fields: {', '.join(missing_fields)}"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get or create category
            category = None
            category_name = data.get('category_name', 'Без категории')
            if category_name and category_name != 'Без категории':
                category, created = Group.objects.get_or_create(
                    name=category_name,
                    defaults={'store': user_store}
                )
            
            # Get or create UOM (Unit of Measure)
            uom, created = Uom.objects.get_or_create(
                name='шт',
                defaults={'description': 'штука'}
            )
            
            # Create the product
            product = Item.objects.create(
                name=data['name'],
                default_price=float(data['price']),
                description=data.get('description', ''),
                status=data.get('status', True),
                store=user_store,
                group=category,
                uom=uom
            )
            
            return Response({
                "id": product.id,
                "name": product.name,
                "price": float(product.default_price),
                "description": product.description,
                "status": "active" if product.status else "inactive",
                "category": category.name if category else "Без категории",
                "created_at": product.created_at.isoformat(),
                "message": "Product created successfully"
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {"detail": f"Error creating product: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class StockRegistrationAPIView(APIView):
    """
    Stock registration (Оприходование) API
    GET /api/v1/seller/inventory/registration/ - List stock registrations
    POST /api/v1/seller/inventory/registration/ - Create stock registration
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get list of stock registrations for user's store"""
        try:
            user_store = getattr(request, 'user_store', None)
            if not user_store:
                try:
                    user_store = Store.objects.get(owner=request.user)
                except Store.DoesNotExist:
                    return Response(
                        {"detail": "У пользователя нет магазина"}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            # Get all storages for user's store
            storages = Storage.objects.filter(store=user_store)
            
            # Get stock registrations for user's storages
            registrations = Enter.objects.filter(
                storage__in=storages
            ).select_related('item', 'storage').order_by('-created_at')
            
            data = []
            for reg in registrations:
                data.append({
                    "id": reg.id,
                    "document_number": reg.document_number or f"REG-{reg.id:03d}",
                    "item_name": reg.item.name,
                    "storage_name": reg.storage.name,
                    "amount": reg.amount,
                    "supplier": reg.supplier or "Не указан",
                    "created_at": reg.created_at.strftime("%d.%m.%Y"),
                    "notes": reg.notes or "",
                    "status": "Исполнен"
                })
            
            return Response(data)
        except Exception as e:
            return Response(
                {"detail": f"Error: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """Create new stock registration"""
        try:
            user_store = getattr(request, 'user_store', None)
            if not user_store:
                try:
                    user_store = Store.objects.get(owner=request.user)
                except Store.DoesNotExist:
                    return Response(
                        {"detail": "У пользователя нет магазина"}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            data = request.data
            
            # Validate required fields
            required_fields = ['item_id', 'storage_id', 'amount']
            missing_fields = [field for field in required_fields if not data.get(field)]
            if missing_fields:
                return Response(
                    {"detail": f"Missing required fields: {', '.join(missing_fields)}"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get item and storage
            try:
                item = Item.objects.get(id=data['item_id'], store=user_store)
                storage = Storage.objects.get(id=data['storage_id'], store=user_store)
            except (Item.DoesNotExist, Storage.DoesNotExist):
                return Response(
                    {"detail": "Товар или склад не найден"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Create stock registration
            registration = Enter.objects.create(
                item=item,
                storage=storage,
                amount=int(data['amount']),
                document_number=data.get('document_number'),
                supplier=data.get('supplier'),
                notes=data.get('notes')
            )
            
            return Response({
                "id": registration.id,
                "document_number": registration.document_number or f"REG-{registration.id:03d}",
                "item_name": registration.item.name,
                "storage_name": registration.storage.name,
                "amount": registration.amount,
                "supplier": registration.supplier or "Не указан",
                "created_at": registration.created_at.strftime("%d.%m.%Y"),
                "message": "Stock registration created successfully"
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {"detail": f"Error creating stock registration: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class WriteOffAPIView(APIView):
    """
    Write-off (Списание) API
    GET /api/v1/seller/inventory/write-offs/ - List write-offs
    POST /api/v1/seller/inventory/write-offs/ - Create write-off
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get list of write-offs for user's store"""
        try:
            user_store = getattr(request, 'user_store', None)
            if not user_store:
                try:
                    user_store = Store.objects.get(owner=request.user)
                except Store.DoesNotExist:
                    return Response(
                        {"detail": "У пользователя нет магазина"}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            # Get all storages for user's store
            storages = Storage.objects.filter(store=user_store)
            
            # Get write-offs for user's storages
            write_offs = WriteOff.objects.filter(
                storage__in=storages
            ).select_related('item', 'storage').order_by('-created_at')
            
            data = []
            for wo in write_offs:
                data.append({
                    "id": wo.id,
                    "document_number": wo.document_number or f"WO-{wo.id:03d}",
                    "item_name": wo.item.name,
                    "storage_name": wo.storage.name,
                    "amount": wo.amount,
                    "reason": wo.reason or "Не указана",
                    "created_at": wo.created_at.strftime("%d.%m.%Y"),
                    "notes": wo.notes or "",
                    "status": "Исполнен"
                })
            
            return Response(data)
        except Exception as e:
            return Response(
                {"detail": f"Error: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """Create new write-off"""
        try:
            user_store = getattr(request, 'user_store', None)
            if not user_store:
                try:
                    user_store = Store.objects.get(owner=request.user)
                except Store.DoesNotExist:
                    return Response(
                        {"detail": "У пользователя нет магазина"}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            data = request.data
            
            # Validate required fields
            required_fields = ['item_id', 'storage_id', 'amount']
            missing_fields = [field for field in required_fields if not data.get(field)]
            if missing_fields:
                return Response(
                    {"detail": f"Missing required fields: {', '.join(missing_fields)}"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get item and storage
            try:
                item = Item.objects.get(id=data['item_id'], store=user_store)
                storage = Storage.objects.get(id=data['storage_id'], store=user_store)
            except (Item.DoesNotExist, Storage.DoesNotExist):
                return Response(
                    {"detail": "Товар или склад не найден"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Check if enough stock available
            try:
                stock = Stock.objects.get(item=item, storage=storage)
                if stock.amount < int(data['amount']):
                    return Response(
                        {"detail": f"Недостаточно товара на складе. Доступно: {stock.amount}"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except Stock.DoesNotExist:
                return Response(
                    {"detail": "Товар отсутствует на складе"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create write-off
            write_off = WriteOff.objects.create(
                item=item,
                storage=storage,
                amount=int(data['amount']),
                document_number=data.get('document_number'),
                reason=data.get('reason'),
                notes=data.get('notes')
            )
            
            return Response({
                "id": write_off.id,
                "document_number": write_off.document_number or f"WO-{write_off.id:03d}",
                "item_name": write_off.item.name,
                "storage_name": write_off.storage.name,
                "amount": write_off.amount,
                "reason": write_off.reason or "Не указана",
                "created_at": write_off.created_at.strftime("%d.%m.%Y"),
                "message": "Write-off created successfully"
            }, status=status.HTTP_201_CREATED)
            
        except ValueError as e:
            return Response(
                {"detail": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"detail": f"Error creating write-off: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class InventoryCheckAPIView(APIView):
    """
    Inventory check (Инвентаризация) API
    GET /api/v1/seller/inventory/checks/ - List inventory checks
    POST /api/v1/seller/inventory/checks/ - Create inventory check
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get list of inventory checks for user's store"""
        try:
            user_store = getattr(request, 'user_store', None)
            if not user_store:
                try:
                    user_store = Store.objects.get(owner=request.user)
                except Store.DoesNotExist:
                    return Response(
                        {"detail": "У пользователя нет магазина"}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            # Get all storages for user's store
            storages = Storage.objects.filter(store=user_store)
            
            # Get inventory checks for user's storages
            checks = InventoryCheck.objects.filter(
                storage__in=storages
            ).select_related('storage').order_by('-created_at')
            
            data = []
            for check in checks:
                # Count items in this check
                items_count = InventoryCheckItem.objects.filter(inventory_check=check).count()
                
                data.append({
                    "id": check.id,
                    "document_number": check.document_number or f"INV-{check.id:03d}",
                    "storage_name": check.storage.name,
                    "items_count": items_count,
                    "status": check.get_status_display(),
                    "created_at": check.created_at.strftime("%d.%m.%Y"),
                    "notes": check.notes or ""
                })
            
            return Response(data)
        except Exception as e:
            return Response(
                {"detail": f"Error: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """Create new inventory check"""
        try:
            user_store = getattr(request, 'user_store', None)
            if not user_store:
                try:
                    user_store = Store.objects.get(owner=request.user)
                except Store.DoesNotExist:
                    return Response(
                        {"detail": "У пользователя нет магазина"}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            data = request.data
            
            # Validate required fields
            if not data.get('storage_id'):
                return Response(
                    {"detail": "Missing required field: storage_id"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get storage
            try:
                storage = Storage.objects.get(id=data['storage_id'], store=user_store)
            except Storage.DoesNotExist:
                return Response(
                    {"detail": "Склад не найден"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Create inventory check
            check = InventoryCheck.objects.create(
                storage=storage,
                document_number=data.get('document_number'),
                notes=data.get('notes')
            )
            
            # Auto-create items for all products in this storage
            stocks = Stock.objects.filter(storage=storage)
            for stock in stocks:
                InventoryCheckItem.objects.create(
                    inventory_check=check,
                    item=stock.item,
                    expected_amount=stock.amount,
                    actual_amount=0  # To be filled during inventory
                )
            
            return Response({
                "id": check.id,
                "document_number": check.document_number or f"INV-{check.id:03d}",
                "storage_name": check.storage.name,
                "status": check.get_status_display(),
                "created_at": check.created_at.strftime("%d.%m.%Y"),
                "message": "Inventory check created successfully"
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {"detail": f"Error creating inventory check: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ItemsListAPIView(APIView):
    """
    Get items list for inventory operations
    GET /api/v1/seller/items/ - List items for current user's store
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get list of items for user's store"""
        try:
            user_store = getattr(request, 'user_store', None)
            if not user_store:
                try:
                    user_store = Store.objects.get(owner=request.user)
                except Store.DoesNotExist:
                    return Response(
                        {"detail": "У пользователя нет магазина"}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            items = Item.objects.filter(store=user_store, status=True)
            
            data = []
            for item in items:
                data.append({
                    "id": item.id,
                    "name": item.name,
                    "uom": item.uom.name if item.uom else "шт."
                })
            
            return Response(data)
        except Exception as e:
            return Response(
                {"detail": f"Error: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class StoragesListAPIView(APIView):
    """
    Get storages list for inventory operations
    GET /api/v1/seller/storages/ - List storages for current user's store
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get list of storages for user's store"""
        try:
            user_store = getattr(request, 'user_store', None)
            if not user_store:
                try:
                    user_store = Store.objects.get(owner=request.user)
                except Store.DoesNotExist:
                    return Response(
                        {"detail": "У пользователя нет магазина"}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            storages = Storage.objects.filter(store=user_store)
            
            data = []
            for storage in storages:
                data.append({
                    "id": storage.id,
                    "name": storage.name,
                    "address": storage.address
                })
            
            return Response(data)
        except Exception as e:
            return Response(
                {"detail": f"Error: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
