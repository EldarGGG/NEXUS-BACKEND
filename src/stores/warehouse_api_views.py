from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Count
from .models import Store, Item, Stock, Storage

class WarehouseStockAPIView(APIView):
    """
    Get warehouse stock overview
    GET /api/v1/warehouse/stock/
    """
    def get(self, request):
        try:
            # For now, we'll get all items and their stock
            # Later this can be filtered by user's store
            
            # Get all items with their stock information
            items_with_stock = []
            
            items = Item.objects.filter(status=True).select_related('group', 'uom')
            
            for item in items:
                # Calculate total stock across all storages for this item
                stocks = Stock.objects.filter(item=item).select_related('storage')
                total_amount = stocks.aggregate(total=Sum('amount'))['total'] or 0
                
                # Get stock by storage
                storages_data = []
                for stock in stocks:
                    storages_data.append({
                        'storage_name': stock.storage.name,
                        'amount': stock.amount
                    })
                
                item_data = {
                    'item_id': item.id,
                    'item_name': item.name,
                    'item_preview': item.preview.url if item.preview else None,
                    'item_price': float(item.default_price),
                    'item_uom': item.uom.name if item.uom else 'шт',
                    'item_category': item.group.name if item.group else 'Без категории',
                    'total_amount': total_amount,
                    'storages': storages_data
                }
                items_with_stock.append(item_data)
            
            return Response(items_with_stock)
            
        except Exception as e:
            return Response(
                {"detail": f"Error: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class WarehouseStatsAPIView(APIView):
    """
    Get warehouse statistics
    GET /api/v1/warehouse/stats/
    """
    def get(self, request):
        try:
            # Calculate warehouse statistics
            total_products = Item.objects.filter(status=True).count()
            
            # Total stock across all items
            total_stock = Stock.objects.aggregate(total=Sum('amount'))['total'] or 0
            
            # Low stock items (less than or equal to 5)
            low_stock_items = 0
            items = Item.objects.filter(status=True)
            for item in items:
                item_total = Stock.objects.filter(item=item).aggregate(total=Sum('amount'))['total'] or 0
                if item_total <= 5:
                    low_stock_items += 1
            
            # Recent movements (placeholder - would need movement tracking)
            recent_movements = 0  # This would be calculated from Enter/WriteOff models
            
            stats = {
                'totalProducts': total_products,
                'totalStock': total_stock,
                'lowStockItems': low_stock_items,
                'recentMovements': recent_movements
            }
            
            return Response(stats)
            
        except Exception as e:
            return Response(
                {"detail": f"Error: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
