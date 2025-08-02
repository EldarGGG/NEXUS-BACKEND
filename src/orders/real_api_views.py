from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from .models import Order, OrderItem, Task, TaskCategory, Counterparty
from stores.models import Store, Item, CounterpartyGroup, CounterpartyMember
from users.models import CustomUser


class RealDashboardStatsAPIView(APIView):
    """
    Real dashboard statistics from database
    GET /api/v1/dashboard/stats/
    """
    permission_classes = [IsAuthenticated]  # Require authentication
    
    def get(self, request):
        try:
            # For testing without authentication, get first available store
            try:
                store = Store.objects.first()
                if not store:
                    return Response(
                        {"detail": "No stores found"}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
            except Exception as e:
                return Response(
                    {"detail": f"Error finding store: {str(e)}"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Базовые статистики заказов
            total_orders = Order.objects.filter(store=store).count()
            pending_orders = Order.objects.filter(store=store, status='pending').count()
            completed_orders = Order.objects.filter(store=store, status='delivered').count()
            
            # Общая выручка
            total_revenue = Order.objects.filter(
                store=store, 
                status__in=['delivered', 'processing', 'shipped']
            ).aggregate(total=Sum('total_price'))['total'] or 0
            
            # Статистики за сегодня
            today = timezone.now().date()
            today_orders = Order.objects.filter(
                store=store, 
                created_at__date=today
            ).count()
            
            today_revenue = Order.objects.filter(
                store=store, 
                created_at__date=today,
                status__in=['delivered', 'processing', 'shipped']
            ).aggregate(total=Sum('total_price'))['total'] or 0
            
            # Количество товаров
            total_products = Item.objects.filter(store=store, status=True).count()
            
            # Топ товары (по количеству заказов)
            top_products = OrderItem.objects.filter(
                order__store=store
            ).values(
                'item__name'
            ).annotate(
                sales=Sum('amount')
            ).order_by('-sales')[:3]
            
            # Последняя активность
            recent_orders = Order.objects.filter(store=store).order_by('-created_at')[:3]
            recent_activity = []
            
            for order in recent_orders:
                recent_activity.append({
                    "type": "order",
                    "message": f"Новый заказ #{order.order_number}",
                    "timestamp": order.created_at.isoformat()
                })
            
            # Добавляем недавно добавленные товары
            recent_products = Item.objects.filter(store=store).order_by('-created_at')[:2]
            for product in recent_products:
                recent_activity.append({
                    "type": "product", 
                    "message": f"Товар \"{product.name}\" добавлен",
                    "timestamp": product.created_at.isoformat()
                })
            
            # Сортируем по времени
            recent_activity = sorted(recent_activity, key=lambda x: x['timestamp'], reverse=True)[:5]
            
            stats = {
                "totalOrders": total_orders,
                "totalProducts": total_products,
                "totalRevenue": float(total_revenue),
                "pendingOrders": pending_orders,
                "completedOrders": completed_orders,
                "todayOrders": today_orders,
                "todayRevenue": float(today_revenue),
                "topProducts": [
                    {"name": item['item__name'], "sales": item['sales']} 
                    for item in top_products
                ],
                "recentActivity": recent_activity
            }
            
            return Response(stats)
            
        except Exception as e:
            return Response(
                {"detail": f"Error: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RealOrdersListAPIView(APIView):
    """
    Real orders list from database
    GET /api/v1/seller/orders/
    """
    permission_classes = [AllowAny]  # Temporarily allow any for testing
    
    def get(self, request):
        try:
            # For testing without authentication, get first available store
            try:
                store = Store.objects.first()
                if not store:
                    return Response(
                        {"detail": "No stores found"}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
            except Exception as e:
                return Response(
                    {"detail": f"Error finding store: {str(e)}"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            orders = Order.objects.filter(store=store).prefetch_related('items__item')
            orders_data = []
            
            for order in orders:
                order_items = []
                for item in order.items.all():
                    order_items.append({
                        "name": item.item.name,
                        "quantity": item.amount,
                        "price": float(item.price_per_item),
                        "total": float(item.total_price)
                    })
                
                orders_data.append({
                    "id": order.id,
                    "order_number": order.order_number,
                    "customer": order.user.email,
                    "customer_name": f"{order.user.first_name} {order.user.last_name}".strip() or order.user.email,
                    "total": float(order.total_price),
                    "status": order.status,
                    "status_display": order.get_status_display(),
                    "created_at": order.created_at.isoformat(),
                    "updated_at": order.updated_at.isoformat(),
                    "comment": order.comment,
                    "delivery_address": order.delivery_address,
                    "items": order_items
                })
            
            return Response(orders_data)
            
        except Exception as e:
            return Response(
                {"detail": f"Error: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RealProductsListAPIView(APIView):
    """
    Real products list from database
    GET /api/v1/seller/products/
    """
    permission_classes = [AllowAny]  # Temporarily allow any for testing
    
    def get(self, request):
        try:
            # For testing without authentication, get first available store
            try:
                store = Store.objects.first()
                if not store:
                    return Response(
                        {"detail": "No stores found"}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
            except Exception as e:
                return Response(
                    {"detail": f"Error finding store: {str(e)}"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            products = Item.objects.filter(store=store)
            products_data = []
            
            for product in products:
                # Получаем остатки на складе
                from stores.models import Stock
                stock_total = Stock.objects.filter(item=product).aggregate(
                    total=Sum('amount')
                )['total'] or 0
                
                # Получаем категорию
                category_name = product.group.name if product.group else "Без категории"
                
                products_data.append({
                    "id": product.id,
                    "name": product.name,
                    "description": product.description,
                    "price": float(product.default_price),
                    "stock": stock_total,
                    "category": category_name,
                    "status": "active" if product.status else "inactive",
                    "image": product.preview.url if product.preview else None,
                    "created_at": product.created_at.isoformat(),
                    "uom": product.uom.name if product.uom else "шт"
                })
            
            return Response(products_data)
            
        except Exception as e:
            return Response(
                {"detail": f"Error: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TasksAPIView(APIView):
    """
    Real tasks management API
    GET /api/v1/seller/tasks/ - List tasks
    POST /api/v1/seller/tasks/ - Create task
    """
    permission_classes = [AllowAny]  # Temporarily allow any for testing
    
    def get(self, request):
        try:
            # For testing without authentication, get first available store
            # TODO: Replace with proper user authentication
            try:
                store = Store.objects.first()
                if not store:
                    return Response(
                        {"detail": "No stores found"}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
            except Exception as e:
                return Response(
                    {"detail": f"Error finding store: {str(e)}"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            tasks = Task.objects.filter(store=store).select_related('category', 'assigned_to', 'created_by')
            tasks_data = []
            
            for task in tasks:
                tasks_data.append({
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "priority": task.priority,
                    "priority_display": task.get_priority_display(),
                    "status": task.status,
                    "status_display": task.get_status_display(),
                    "category": {
                        "id": task.category.id,
                        "name": task.category.name,
                        "color": task.category.color
                    } if task.category else None,
                    "assigned_to": {
                        "id": task.assigned_to.id,
                        "email": task.assigned_to.email,
                        "name": f"{task.assigned_to.first_name} {task.assigned_to.last_name}".strip()
                    },
                    "created_by": {
                        "id": task.created_by.id,
                        "email": task.created_by.email,
                        "name": f"{task.created_by.first_name} {task.created_by.last_name}".strip()
                    },
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat(),
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                    "estimated_hours": float(task.estimated_hours) if task.estimated_hours else None,
                    "actual_hours": float(task.actual_hours) if task.actual_hours else None
                })
            
            return Response(tasks_data)
            
        except Exception as e:
            return Response(
                {"detail": f"Error: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        try:
            # For testing without authentication, get first available store and user
            # TODO: Replace with proper user authentication
            try:
                store = Store.objects.first()
                if not store:
                    return Response(
                        {"detail": "No stores found"}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
                user = store.owner  # Use store owner as current user
            except Exception as e:
                return Response(
                    {"detail": f"Error finding store: {str(e)}"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            data = request.data
            
            # Создаем задачу для конкретного магазина
            task = Task.objects.create(
                title=data.get('title'),
                description=data.get('description', ''),
                priority=data.get('priority', 'medium'),
                store=store,  # Привязываем к конкретному магазину
                assigned_to=user,  # Назначаем владельцу магазина
                created_by=user   # Создано владельцем магазина
            )
            
            # Если указана категория
            if data.get('category_id'):
                try:
                    category = TaskCategory.objects.get(id=data['category_id'])
                    task.category = category
                    task.save()
                except TaskCategory.DoesNotExist:
                    pass
            
            return Response({
                "id": task.id,
                "title": task.title,
                "status": task.status,
                "created_at": task.created_at.isoformat()
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {"detail": f"Error: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ContractorsAPIView(APIView):
    """
    Contractors/Counterparties management API
    GET /api/v1/seller/contractors/ - List contractors
    POST /api/v1/seller/contractors/ - Create contractor
    """
    permission_classes = [AllowAny]  # Temporarily allow any for testing
    
    def get(self, request):
        try:
            # For testing without authentication, get first available store
            # TODO: Replace with proper user authentication
            try:
                store = Store.objects.first()
                if not store:
                    return Response(
                        {"detail": "No stores found"}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
            except Exception as e:
                return Response(
                    {"detail": f"Error finding store: {str(e)}"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Получаем контрагентов для данного магазина
            contractors = Counterparty.objects.filter(store=store)
            contractors_data = []
            
            for contractor in contractors:
                contractors_data.append({
                    "id": contractor.id,
                    "name": contractor.name,
                    "email": contractor.email,
                    "phone": contractor.phone,
                    "address": contractor.address,
                    "type": contractor.type,
                    "type_display": contractor.get_type_display(),
                    "status": contractor.status,
                    "status_display": contractor.get_status_display(),
                    "created_at": contractor.created_at.isoformat(),
                    "total_orders": contractor.total_orders,
                    "total_spent": contractor.total_spent,
                    "last_order_date": contractor.last_order_date.isoformat() if contractor.last_order_date else None
                })
            
            return Response(contractors_data)
            
        except Exception as e:
            return Response(
                {"detail": f"Error: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        try:
            # For testing without authentication, get first available store and user
            # TODO: Replace with proper user authentication
            try:
                store = Store.objects.first()
                if not store:
                    return Response(
                        {"detail": "No stores found"}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
            except Exception as e:
                return Response(
                    {"detail": f"Error finding store: {str(e)}"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            data = request.data
            
            # Создаем контрагента для конкретного магазина
            contractor = Counterparty.objects.create(
                name=data.get('name'),
                email=data.get('email'),
                phone=data.get('phone', ''),
                address=data.get('address', ''),
                type=data.get('type', 'customer'),
                store=store  # Привязываем к конкретному магазину
            )
            
            return Response({
                "id": contractor.id,
                "name": contractor.name,
                "email": contractor.email,
                "type": contractor.type,
                "created_at": contractor.created_at.isoformat()
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {"detail": f"Error: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AnalyticsAPIView(APIView):
    """
    Real analytics data from database
    GET /api/v1/seller/analytics/
    """
    permission_classes = [AllowAny]  # Temporarily allow any for testing
    
    def get(self, request):
        try:
            # For testing without authentication, get first available store
            try:
                store = Store.objects.first()
                if not store:
                    return Response(
                        {"detail": "No stores found"}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
            except Exception as e:
                return Response(
                    {"detail": f"Error finding store: {str(e)}"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Период для анализа (последние 30 дней)
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=30)
            
            # Продажи по дням
            daily_sales = []
            current_date = start_date
            while current_date <= end_date:
                day_orders = Order.objects.filter(
                    store=store,
                    created_at__date=current_date,
                    status__in=['delivered', 'processing', 'shipped']
                )
                
                day_revenue = day_orders.aggregate(total=Sum('total_price'))['total'] or 0
                day_count = day_orders.count()
                
                daily_sales.append({
                    "date": current_date.isoformat(),
                    "revenue": float(day_revenue),
                    "orders_count": day_count
                })
                
                current_date += timedelta(days=1)
            
            # Топ товары за период
            top_products = OrderItem.objects.filter(
                order__store=store,
                order__created_at__date__gte=start_date
            ).values(
                'item__name', 'item__id'
            ).annotate(
                total_sold=Sum('amount'),
                total_revenue=Sum('total_price')
            ).order_by('-total_revenue')[:10]
            
            # Статистика по статусам заказов
            order_status_stats = Order.objects.filter(
                store=store,
                created_at__date__gte=start_date
            ).values('status').annotate(count=Count('id'))
            
            analytics_data = {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "daily_sales": daily_sales,
                "top_products": [
                    {
                        "id": item['item__id'],
                        "name": item['item__name'],
                        "total_sold": item['total_sold'],
                        "total_revenue": float(item['total_revenue'])
                    }
                    for item in top_products
                ],
                "order_status_distribution": [
                    {
                        "status": item['status'],
                        "count": item['count']
                    }
                    for item in order_status_stats
                ],
                "summary": {
                    "total_revenue": float(sum(day['revenue'] for day in daily_sales)),
                    "total_orders": sum(day['orders_count'] for day in daily_sales),
                    "average_order_value": float(sum(day['revenue'] for day in daily_sales) / max(sum(day['orders_count'] for day in daily_sales), 1))
                }
            }
            
            return Response(analytics_data)
            
        except Exception as e:
            return Response(
                {"detail": f"Error: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
