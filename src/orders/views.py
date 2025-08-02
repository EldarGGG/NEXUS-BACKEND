from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema_view, extend_schema

from stores.models import Item, SelfPickupPoint, Store, Stock
from users.models import CustomUser
from .models import Cart, CartItem, Order, OrderItem
from .serializers import *
from orders import schemas


class ProtectedView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(**schemas.protected_route)
    def get(self, request, format=None):
        content = {
            'message': 'Успешный доступ к защищеному роуту',
            'user': str(request.user),  # `django.contrib.auth.User` instance.
            'auth': str(request.auth),  # None
        }
        return Response(content)


@extend_schema_view(**schemas.stock_schemas)
class StockAPIView(APIView):
    def get(self, request, *args, **kwargs):
        stocks = Stock.objects.filter(item_id=kwargs.get("item_id"))
        return Response(
            {
                "stocks": StockSerializer(stocks, many=True).data
            }
        )


@extend_schema_view(**schemas.orders_post_schema)
class OrderCreationAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            Cart.objects.get(user_id=request.user.id)
        except Cart.DoesNotExist:
            return Response({'status': 'error. cart does not exist'})

        cart_items = CartItem.objects.filter(cart__user=request.user)
        if len(cart_items) == 0:
            return Response({'status': 'error. cart is empty'})

        total_price = 0
        for cart_item in cart_items:
            total_price += cart_item.item.default_price * cart_item.amount

        new_order = Order.objects.create(
            user=request.user,
            self_pickup_point=SelfPickupPoint.objects.get(id=request.data["self_pickup_point"]),
            comment=request.data["comment"],
            status="принят",
            total_price=total_price
        )
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=new_order,
                item=cart_item.item,
                amount=cart_item.amount
            )
        cart_items.delete()
        return Response({'status': 'order created'})


@extend_schema_view(**schemas.orders_schemas)
class OrderAPIView(viewsets.ReadOnlyModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def list(self, request):
        request.jwt_user = CustomUser.objects.get(id=request.user.id)
        queryset = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Order.objects.get(id=pk)
        serializer = OrderSerializer(queryset)
        return Response(serializer.data)


@extend_schema_view(**schemas.cart_schemas)
class CartAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_cart = Cart.objects.get(user_id=request.user.id)
            cart_items = CartItem.objects.filter(cart=user_cart)
        except Cart.DoesNotExist:
            new_cart = Cart.objects.create(user_id=request.user.id)
            cart_items = CartItem.objects.filter(cart__user_id=request.user.id)
        return Response({"items": CartItemSerializer(cart_items, many=True, context={"request": request}).data})

    def post(self, request):
        try:
            user_cart = Cart.objects.get(user_id=request.user.id)
        except Cart.DoesNotExist:
            user_cart = Cart.objects.create(user_id=request.user.id)

        try:
            item = Item.objects.get(pk=request.data["item"])
        except Item.DoesNotExist:
            return Response({'msg': 'item does not exists!'})

        try:
            cart_item = CartItem.objects.get(cart=user_cart, item__id=item.pk)
            amount = request.data['amount']
            if amount > 0:
                cart_item.amount = amount
                cart_item.save()
                msg = "cart item amount updated"
            else:
                cart_item.delete()
                msg = "cart item deleted"
        except CartItem.DoesNotExist:
            CartItem.objects.create(
                cart=Cart.objects.get(user__id=request.user.id),
                item=item,
                amount=request.data["amount"]
            )
            msg = "new cart item created"

        return Response({'msg': msg})

    def delete(self, request):
        try:
            item = Item.objects.get(pk=request.data["item"])
        except Item.DoesNotExist:
            return Response({'msg': 'item does not exists!'})

        try:
            cart_item = CartItem.objects.get(cart__user_id=request.user.id, item__id=item.pk)
            cart_item.delete()
        except CartItem.DoesNotExist:
            return Response({'msg': 'item does not exists!'})

        return Response({'msg': 'cart item deleted'})


@extend_schema_view(**schemas.stores_schemas)
class StoreAPIView(viewsets.ReadOnlyModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer


@extend_schema_view(**schemas.items_schemas)
class ItemAPIView(viewsets.ReadOnlyModelViewSet):
    serializer_class = ItemSerializer

    def get_queryset(self):
        return Item.objects.filter(store__id=self.kwargs['store_id'])


@extend_schema_view(**schemas.self_pickup_points_schemas)
class SelfPickupPointAPIView(viewsets.ReadOnlyModelViewSet):
    serializer_class = SelfPickupPointSerializer

    def get_queryset(self):
        return SelfPickupPoint.objects.filter(store__id=self.kwargs['store_id'])
