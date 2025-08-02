from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from decimal import Decimal

from .models import Store, Item, Storage, Stock, Group, Uom
from users.models import CustomUser


class SellerProductsAPIView(APIView):
    """
    Seller products management
    GET /api/v1/seller/products/ - Get seller's products
    POST /api/v1/seller/products/ - Create new product with stock
    """
    
    def get(self, request):
        """Get seller's products"""
        try:
            # Get user's store (for now, use first store)
            user = request.user if hasattr(request, 'user') else None
            if not user:
                # For testing, get first user
                user = CustomUser.objects.first()
            
            store = Store.objects.filter(owner=user).first()
            if not store:
                return Response({"detail": "Store not found"}, status=status.HTTP_404_NOT_FOUND)
            
            # Get all items for this store with stock information
            items = Item.objects.filter(store=store).prefetch_related('stock_set__storage')
            
            products_data = []
            for item in items:
                # Calculate total stock across all storages
                total_stock = sum(stock.amount for stock in item.stock_set.all())
                
                products_data.append({
                    "id": item.id,
                    "name": item.name,
                    "description": item.description or "",
                    "price": float(item.default_price) if item.default_price else 0,
                    "stock": total_stock,
                    "category": item.group.name if item.group else "Без категории",
                    "status": "active" if item.status else "inactive",
                    "created_at": item.created_at.isoformat() if hasattr(item, 'created_at') else "",
                    "uom": item.uom.name if item.uom else "шт",
                    "storages": [
                        {
                            "storage_name": stock.storage.name,
                            "amount": stock.amount
                        }
                        for stock in item.stock_set.all()
                    ]
                })
            
            return Response(products_data)
            
        except Exception as e:
            return Response(
                {"detail": f"Error: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """Create new product with stock"""
        try:
            data = request.data
            
            # Get user's store
            user = request.user if hasattr(request, 'user') else None
            if not user:
                # For testing, get first user
                user = CustomUser.objects.first()
            
            store = Store.objects.filter(owner=user).first()
            if not store:
                return Response({"detail": "Store not found"}, status=status.HTTP_404_NOT_FOUND)
            
            # Validate required fields
            required_fields = ['name', 'price', 'warehouse_id', 'quantity']
            for field in required_fields:
                if field not in data or not data[field]:
                    return Response(
                        {"detail": f"Field '{field}' is required"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Get or create category group
            category_name = data.get('category_name', 'Без категории')
            group, _ = Group.objects.get_or_create(
                name=category_name,
                store=store,
                defaults={'description': f'Группа {category_name}'}
            )
            
            # Get or create default UOM
            uom, _ = Uom.objects.get_or_create(
                name='шт',
                defaults={'description': 'Штуки'}
            )
            
            # Get warehouse and quantity for stock creation
            warehouse_id = data.get('warehouse_id')
            quantity = data.get('quantity', 0)
            
            # Warehouse is required - validate it exists and belongs to store
            try:
                warehouse = Storage.objects.get(id=warehouse_id, store=store)
            except Storage.DoesNotExist:
                return Response(
                    {"detail": "Warehouse not found or does not belong to your store"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Create item and stock in a transaction
            with transaction.atomic():
                # Create item with required default_storage
                item = Item.objects.create(
                    name=data['name'],
                    description=data.get('description', ''),
                    default_price=Decimal(str(data['price'])),
                    store=store,
                    group=group,
                    uom=uom,
                    status=data.get('status', True),
                    default_storage=warehouse  # Устанавливаем обязательный склад по умолчанию
                )
                
                # Always create stock record since warehouse is required
                stock = Stock.objects.create(
                    item=item,
                    storage=warehouse,
                    amount=quantity
                )
            
            return Response({
                "id": item.id,
                "name": item.name,
                "warehouse": warehouse.name,
                "message": "Product created successfully"
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {"detail": f"Error creating product: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class WarehousesAPIView(APIView):
    """
    Get warehouses/storages for seller
    GET /api/v1/warehouses/
    """
    
    def get(self, request):
        """Get seller's warehouses"""
        try:
            # Get user's store
            user = request.user if hasattr(request, 'user') else None
            if not user:
                # For testing, get first user
                user = CustomUser.objects.first()
            
            store = Store.objects.filter(owner=user).first()
            if not store:
                return Response({"detail": "Store not found"}, status=status.HTTP_404_NOT_FOUND)
            
            # Get all storages for this store
            storages = Storage.objects.filter(store=store)
            
            warehouses_data = [
                {
                    "id": storage.id,
                    "name": storage.name,
                    "description": storage.description or "",
                    "address": storage.address or ""
                }
                for storage in storages
            ]
            
            return Response(warehouses_data)
            
        except Exception as e:
            return Response(
                {"detail": f"Error: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        """Create a new warehouse for the authenticated user's store"""
        try:
            store = Store.objects.get(owner=request.user)
            
            name = request.data.get('name')
            description = request.data.get('description', '')
            address = request.data.get('address', '')
            
            if not name:
                return Response({'error': 'Name is required'}, status=400)
            
            # Create new warehouse
            warehouse = Storage.objects.create(
                store=store,
                name=name,
                description=description,
                address=address
            )
            
            return Response({
                'id': warehouse.id,
                'name': warehouse.name,
                'description': warehouse.description,
                'address': warehouse.address,
                'message': 'Warehouse created successfully'
            }, status=201)
            
        except Store.DoesNotExist:
            return Response({'error': 'Store not found'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class WarehouseDetailAPIView(APIView):
    """
    Manage individual warehouse operations
    GET /api/v1/warehouses/{id}/ - Get warehouse details
    PUT /api/v1/warehouses/{id}/ - Update warehouse
    DELETE /api/v1/warehouses/{id}/ - Delete warehouse
    """
    
    def get(self, request, warehouse_id):
        """Get warehouse details"""
        try:
            # Get user's store
            user = request.user if hasattr(request, 'user') else None
            if not user:
                # For testing, get first user
                user = CustomUser.objects.first()
            
            store = Store.objects.filter(owner=user).first()
            if not store:
                return Response({"detail": "Store not found"}, status=status.HTTP_404_NOT_FOUND)
            
            # Get storage by id and check ownership
            try:
                storage = Storage.objects.get(id=warehouse_id, store=store)
            except Storage.DoesNotExist:
                return Response({"detail": "Warehouse not found"}, status=status.HTTP_404_NOT_FOUND)
            
            # Count items in this storage
            item_count = Stock.objects.filter(storage=storage).count()
            
            warehouse_data = {
                "id": storage.id,
                "name": storage.name,
                "description": storage.description or "",
                "address": storage.address or "",
                "item_count": item_count,
                "created_at": storage.created_at.strftime("%Y-%m-%d") if hasattr(storage, 'created_at') else ""
            }
            
            return Response(warehouse_data)
            
        except Exception as e:
            return Response(
                {"detail": f"Error: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def put(self, request, warehouse_id):
        """Update warehouse details"""
        try:
            # Get user's store
            user = request.user
            store = Store.objects.filter(owner=user).first()
            if not store:
                return Response({"detail": "Store not found"}, status=status.HTTP_404_NOT_FOUND)
            
            # Get storage by id and check ownership
            try:
                storage = Storage.objects.get(id=warehouse_id, store=store)
            except Storage.DoesNotExist:
                return Response({"detail": "Warehouse not found"}, status=status.HTTP_404_NOT_FOUND)
            
            # Update warehouse fields
            if 'name' in request.data:
                storage.name = request.data['name']
            if 'description' in request.data:
                storage.description = request.data['description']
            if 'address' in request.data:
                storage.address = request.data['address']
                
            storage.save()
            
            # Count items in this storage
            item_count = Stock.objects.filter(storage=storage).count()
            
            warehouse_data = {
                "id": storage.id,
                "name": storage.name,
                "description": storage.description or "",
                "address": storage.address or "",
                "item_count": item_count,
                "message": "Warehouse updated successfully"
            }
            
            return Response(warehouse_data)
            
        except Exception as e:
            return Response(
                {"detail": f"Error updating warehouse: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request, warehouse_id):
        """Delete warehouse"""
        try:
            # Get user's store
            user = request.user
            store = Store.objects.filter(owner=user).first()
            if not store:
                return Response({"detail": "Store not found"}, status=status.HTTP_404_NOT_FOUND)
            
            # Get storage by id and check ownership
            try:
                storage = Storage.objects.get(id=warehouse_id, store=store)
            except Storage.DoesNotExist:
                return Response({"detail": "Warehouse not found"}, status=status.HTTP_404_NOT_FOUND)
            
            # Check if there are stocks in this warehouse
            stocks = Stock.objects.filter(storage=storage)
            if stocks.exists():
                return Response(
                    {"detail": "Cannot delete warehouse with existing stock. Please move or delete stock items first."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Delete the warehouse
            storage_name = storage.name
            storage.delete()
            
            return Response({
                "detail": f"Warehouse '{storage_name}' deleted successfully"
            })
            
        except Exception as e:
            return Response(
                {"detail": f"Error deleting warehouse: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
