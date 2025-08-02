from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db import transaction
from django.shortcuts import get_object_or_404

from .models import Order, OrderItem, Cart, CartItem
from stores.models import Store, Item
from users.models import CustomUser


class CreateOrderAPIView(APIView):
    """
    Create real order from cart
    POST /api/v1/orders/create/
    """
    permission_classes = [AllowAny]  # Temporarily allow any for testing
    
    def post(self, request):
        try:
            user = request.user
            data = request.data
            
            # Получаем магазин
            store_id = data.get('store_id')
            if not store_id:
                return Response(
                    {"detail": "store_id is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            store = get_object_or_404(Store, id=store_id)
            
            # Получаем корзину пользователя
            try:
                cart = Cart.objects.get(user=user)
                cart_items = CartItem.objects.filter(cart=cart, item__store=store)
                
                if not cart_items.exists():
                    return Response(
                        {"detail": "Cart is empty for this store"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except Cart.DoesNotExist:
                return Response(
                    {"detail": "Cart not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Создаем заказ в транзакции
            with transaction.atomic():
                # Создаем заказ
                order = Order.objects.create(
                    user=user,
                    store=store,
                    comment=data.get('comment', ''),
                    delivery_address=data.get('delivery_address', ''),
                    status='pending'
                )
                
                total_price = 0
                
                # Создаем позиции заказа из корзины
                for cart_item in cart_items:
                    item_price = cart_item.item.default_price
                    item_total = item_price * cart_item.amount
                    
                    OrderItem.objects.create(
                        order=order,
                        item=cart_item.item,
                        amount=cart_item.amount,
                        price_per_item=item_price,
                        total_price=item_total
                    )
                    
                    total_price += item_total
                
                # Обновляем общую стоимость заказа
                order.total_price = total_price
                order.save()
                
                # Очищаем корзину для этого магазина
                cart_items.delete()
                
                return Response({
                    "order_id": order.id,
                    "order_number": order.order_number,
                    "total_price": float(order.total_price),
                    "status": order.status,
                    "created_at": order.created_at.isoformat(),
                    "message": "Order created successfully"
                }, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            return Response(
                {"detail": f"Error creating order: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UpdateOrderStatusAPIView(APIView):
    """
    Update order status
    PUT /api/v1/orders/{order_id}/status/
    """
    permission_classes = [AllowAny]  # Temporarily allow any for testing
    
    def put(self, request, order_id):
        try:
            user = request.user
            
            # Получаем заказ
            try:
                # Если пользователь - владелец магазина, может обновлять заказы своего магазина
                store = Store.objects.get(owner=user)
                order = Order.objects.get(id=order_id, store=store)
            except (Store.DoesNotExist, Order.DoesNotExist):
                # Если пользователь - покупатель, может обновлять только свои заказы
                try:
                    order = Order.objects.get(id=order_id, user=user)
                except Order.DoesNotExist:
                    return Response(
                        {"detail": "Order not found"}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            new_status = request.data.get('status')
            if not new_status:
                return Response(
                    {"detail": "status is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Проверяем валидность статуса
            valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
            if new_status not in valid_statuses:
                return Response(
                    {"detail": f"Invalid status. Valid options: {valid_statuses}"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            order.status = new_status
            order.save()
            
            return Response({
                "order_id": order.id,
                "order_number": order.order_number,
                "status": order.status,
                "status_display": order.get_status_display(),
                "updated_at": order.updated_at.isoformat(),
                "message": "Order status updated successfully"
            })
            
        except Exception as e:
            return Response(
                {"detail": f"Error updating order: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AddToCartAPIView(APIView):
    """
    Add item to cart
    POST /api/v1/cart/add/
    """
    permission_classes = [AllowAny]  # Temporarily allow any for testing
    
    def post(self, request):
        try:
            user = request.user
            data = request.data
            
            item_id = data.get('item_id')
            amount = data.get('amount', 1)
            
            if not item_id:
                return Response(
                    {"detail": "item_id is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Получаем товар
            try:
                item = Item.objects.get(id=item_id)
            except Item.DoesNotExist:
                return Response(
                    {"detail": "Item not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Получаем или создаем корзину
            cart, created = Cart.objects.get_or_create(user=user)
            
            # Получаем или создаем позицию в корзине
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                item=item,
                defaults={'amount': amount}
            )
            
            if not created:
                # Если позиция уже существует, увеличиваем количество
                cart_item.amount += amount
                cart_item.save()
            
            return Response({
                "cart_item_id": cart_item.id,
                "item_name": item.name,
                "amount": cart_item.amount,
                "message": "Item added to cart successfully"
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {"detail": f"Error adding to cart: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RealCartAPIView(APIView):
    """
    Real Cart API with database integration
    GET /api/v1/carts/ - Get cart contents
    POST /api/v1/carts/ - Add item to cart
    DELETE /api/v1/carts/clear/ - Clear cart
    """
    permission_classes = [AllowAny]  # Temporarily allow any for testing
    
    def get(self, request):
        try:
            user = request.user
            
            try:
                cart = Cart.objects.get(user=user)
                cart_items = CartItem.objects.filter(cart=cart).select_related('item', 'item__store', 'item__uom')
            except Cart.DoesNotExist:
                return Response({"items": []})
            
            items_data = []
            for cart_item in cart_items:
                items_data.append({
                    "id": cart_item.id,
                    "amount": cart_item.amount,
                    "item": {
                        "id": cart_item.item.id,
                        "name": cart_item.item.name,
                        "preview": cart_item.item.preview.url if cart_item.item.preview else None,
                        "price": float(cart_item.item.default_price),
                        "store": {
                            "id": cart_item.item.store.id,
                            "name": cart_item.item.store.name
                        },
                        "uom": {
                            "name": cart_item.item.uom.name if cart_item.item.uom else "шт"
                        }
                    }
                })
            
            return Response({"items": items_data})
            
        except Exception as e:
            return Response(
                {"detail": f"Error: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request):
        try:
            user = request.user
            
            try:
                cart = Cart.objects.get(user=user)
                CartItem.objects.filter(cart=cart).delete()
                return Response({"message": "Cart cleared successfully"})
            except Cart.DoesNotExist:
                return Response({"message": "Cart was already empty"})
                
        except Exception as e:
            return Response(
                {"detail": f"Error: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """
        Add item to cart
        """
        try:
            user = request.user
            data = request.data
            
            item_id = data.get('item_id')
            amount = data.get('amount', 1)
            
            if not item_id:
                return Response(
                    {"detail": "item_id is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                item = Item.objects.get(id=item_id)
            except Item.DoesNotExist:
                return Response(
                    {"detail": "Item not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Get or create cart for user
            cart, created = Cart.objects.get_or_create(user=user)
            
            # Check if item already in cart
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                item=item,
                defaults={'amount': amount}
            )
            
            if not created:
                # Item already in cart, update amount
                cart_item.amount += amount
                cart_item.save()
            
            return Response({
                "success": True,
                "message": "Item added to cart",
                "item_id": item_id,
                "amount": cart_item.amount
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {"detail": f"Error adding to cart: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
