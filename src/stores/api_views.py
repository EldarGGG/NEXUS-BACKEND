from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Store, Item, Group, Stock


class StoreDetailAPIView(APIView):
    """
    Get store information
    GET /api/v1/stores/{store_id}/
    """
    def get(self, request, store_id):
        try:
            # Return mock data for now
            return Response({
                "id": store_id,
                "name": f"Test Store {store_id}",
                "description": "Test store description"
            })
        except Exception as e:
            return Response(
                {"detail": f"Error: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class StoreItemsAPIView(APIView):
    """
    Get store items
    GET /api/v1/stores/{store_id}/items/
    """
    def get(self, request, store_id):
        try:
            # Get the store
            try:
                store = Store.objects.get(id=store_id)
            except Store.DoesNotExist:
                return Response(
                    {"detail": "Store not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Get all items for this store
            items = Item.objects.filter(store=store, status=True)
            
            items_data = []
            for item in items:
                # Calculate total stock from all storages
                total_stock = 0
                try:
                    stocks = Stock.objects.filter(item=item)
                    total_stock = sum(stock.amount for stock in stocks)
                except:
                    total_stock = 0
                
                item_data = {
                    "id": item.id,
                    "name": item.name,
                    "preview": item.preview.url if item.preview else None,
                    "amount": float(item.default_price),  # Price field (keeping for frontend compatibility)
                    "price": float(item.default_price),  # Add explicit price field
                    "stock": total_stock,  # Stock quantity
                    "methods": ["card", "cash"],  # Default payment methods
                    "description": item.description,
                    "subcategory": {
                        "name": item.group.name if item.group else "Без категории",
                        "store": store_id,
                        "category": {
                            "name": item.group.name if item.group else "Без категории"
                        }
                    },
                    "uom": {
                        "name": item.uom.name if item.uom else "шт"
                    }
                }
                items_data.append(item_data)
            
            return Response(items_data)
        except Exception as e:
            return Response(
                {"detail": f"Error: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class StoreSubcategoriesAPIView(APIView):
    """
    Get store subcategories
    GET /api/v1/stores/{store_id}/subcategories/
    """
    def get(self, request, store_id):
        try:
            # Return mock subcategories data
            mock_subcategories = [
                {
                    "id": 1,
                    "name": "Electronics",
                    "store": store_id
                },
                {
                    "id": 2, 
                    "name": "Clothing",
                    "store": store_id
                },
                {
                    "id": 3,
                    "name": "Books",
                    "store": store_id
                }
            ]
            return Response(mock_subcategories)
        except Exception as e:
            return Response(
                {"detail": f"Error: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
