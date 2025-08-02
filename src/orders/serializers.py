from django.db.models import Sum

from rest_framework import serializers

from .models import Cart, CartItem, Order, OrderItem
from stores.models import *


class UomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Uom
        fields = ['name']


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ['name', 'icon']


class StoreSerializer(serializers.ModelSerializer):
    payment_methods = serializers.SerializerMethodField('get_payment_methods')

    def get_payment_methods(self, obj):
        q = StorePaymentMethod.objects.filter(store_id=obj.id).values('payment_method')
        res = PaymentMethod.objects.filter(pk__in=q)
        return PaymentMethodSerializer(res, many=True, context=self.context).data

    class Meta:
        model = Store
        fields = "__all__"


class ItemImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)

    class Meta:
        model = ItemImage
        fields = ('description', 'image')


class ItemSerializer(serializers.ModelSerializer):
    uom = UomSerializer()
    amount = serializers.SerializerMethodField('get_amount')
    preview = serializers.ImageField(use_url=True)
    images = serializers.SerializerMethodField('get_images')

    def get_amount(self, obj):
        res = Stock.objects.filter(item_id=obj.id).aggregate(Sum("amount"))
        return res

    def get_images(self, obj):
        res = ItemImage.objects.filter(item__id=obj.id)
        return ItemImageSerializer(res, many=True, context=self.context).data

    class Meta:
        model = Item
        fields = '__all__'


class CartItemSerializer(serializers.ModelSerializer):
    item = ItemSerializer()

    class Meta:
        model = CartItem
        fields = ('item', 'amount')


class SelfPickupPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = SelfPickupPoint
        fields = '__all__'


class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True, source='cartitem_set')

    class Meta:
        model = Cart
        fields = ('user', 'cart_items')


class OrderItemSerializer(serializers.ModelSerializer):
    item = ItemSerializer()

    class Meta:
        model = OrderItem
        fields = ('item', 'amount')


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, source='orderitem_set')

    class Meta:
        model = Order
        fields = "__all__"


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = "__all__"


class StorageSerializer(serializers.ModelSerializer):
    store = StoreSerializer()
    city = CitySerializer()

    class Meta:
        model = Storage
        fields = "__all__"


class StockSerializer(serializers.ModelSerializer):
    storage = StorageSerializer()

    class Meta:
        model = Stock
        fields = "__all__"
