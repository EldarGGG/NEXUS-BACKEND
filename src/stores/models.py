from django.db import models

from users.models import CustomUser


class Store(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    owner = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE)
    logo = models.ImageField(upload_to='images/', null=True, default=None)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Магазин"
        verbose_name_plural = "Магазины"


class Integration(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=220)
    image = models.ImageField(upload_to='images/')
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Интеграция"
        verbose_name_plural = "Интеграции"


class IntegrationStore(models.Model):
    store = models.ForeignKey(to=Store, on_delete=models.CASCADE)
    integration = models.ForeignKey(to=Integration, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.store.name} - {self.integration.name}"

    class Meta:
        verbose_name = "Интеграция магазина"
        verbose_name_plural = "Интеграции магазинов"


class SelfPickupPoint(models.Model):
    name = models.CharField(max_length=120)
    address = models.CharField(max_length=220)
    store = models.ForeignKey(to=Store, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}, {self.store.name} - {self.address}"

    class Meta:
        verbose_name = "Точка самовывоза"
        verbose_name_plural = "Точки самовывоза"


class Group(models.Model):
    store = models.ForeignKey(to=Store, on_delete=models.CASCADE)
    name = models.CharField(max_length=220)
    description = models.CharField(max_length=220, null=True, default=None)
    external_id = models.CharField(max_length=64, unique=True, null=True, default=None)
    parent = models.ForeignKey(to='self', on_delete=models.CASCADE, null=True, default=None)
    is_root = models.BooleanField(null=True, default=None)
    parent_external_id = models.CharField(max_length=64, null=True, default=None)

    def __str__(self):
        return f'{self.name}. Parent: {self.parent}'

    class Meta:
        verbose_name = "Податегория"
        verbose_name_plural = "Подкатегории"


class Uom(models.Model):
    name = models.CharField(max_length=20)
    description = models.TextField(null=True, default=None)
    external_id = models.CharField(max_length=64, unique=True, null=True, default=None)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Единица измерения"
        verbose_name_plural = "Единицы измерения"


class Item(models.Model):
    store = models.ForeignKey(to=Store, on_delete=models.CASCADE)
    group = models.ForeignKey(to=Group, on_delete=models.CASCADE, null=True, default=None)
    description = models.TextField(default="Описание отсутствует")
    name = models.CharField(max_length=220)
    created_at = models.DateField(auto_now_add=True)
    status = models.BooleanField(default=True)
    preview = models.ImageField(upload_to='images/')
    uom = models.ForeignKey(to=Uom, on_delete=models.CASCADE, null=True, default=None)
    default_price = models.DecimalField(max_digits=16, decimal_places=2, default=10)
    # Обязательное поле связи с основным складом товара
    default_storage = models.ForeignKey(to='Storage', on_delete=models.PROTECT, related_name='default_items')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"


class ItemImage(models.Model):
    item = models.ForeignKey(to=Item, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/')
    description = models.CharField(max_length=220)

    def __str__(self):
        return self.item.name

    class Meta:
        verbose_name = "Изображение Товара"
        verbose_name_plural = "Изображения Товаров"


class Currency(models.Model):
    name = models.CharField(max_length=40)
    full_name = models.CharField(max_length=40)
    symbol = models.CharField(max_length=40, null=True, default=None)
    iso_code = models.CharField(max_length=5)
    major_unit = models.CharField(max_length=40)
    minor_unit = models.CharField(max_length=40, null=True, default=None)
    external_id = models.CharField(max_length=64, unique=True, null=True, default=None)

    def __str__(self):
        return f"{self.name} ({self.symbol})"

    class Meta:
        verbose_name = "Валюта"
        verbose_name_plural = "Валюты"


class CounterpartyGroup(models.Model):
    name = models.CharField(max_length=40)
    store = models.ForeignKey(to=Store, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.store.name})"

    class Meta:
        verbose_name = "Группа контрагентов"
        verbose_name_plural = "Группы контрагентов"


class CounterpartyMember(models.Model):
    user = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE)
    counterparty_group = models.ForeignKey(to=CounterpartyGroup, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Контрагент"
        verbose_name_plural = "Контрагенты"


class Price(models.Model):
    item = models.ForeignKey(to=Item, on_delete=models.CASCADE)
    value = models.DecimalField(max_digits=16, decimal_places=2)
    currency = models.ForeignKey(to=Currency, on_delete=models.CASCADE)
    counterparty_group = models.ForeignKey(to=CounterpartyGroup, on_delete=models.CASCADE, null=True, blank=True)


class Country(models.Model):
    name = models.CharField(max_length=40)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Страна"
        verbose_name_plural = "Страны"


class City(models.Model):
    name = models.CharField(max_length=120)
    country = models.ForeignKey(to=Country, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Город"
        verbose_name_plural = "Города"


class Storage(models.Model):
    name = models.CharField(max_length=120)
    city = models.ForeignKey(to=City, on_delete=models.CASCADE)
    address = models.CharField(max_length=200, default='Not provided')
    store = models.ForeignKey(to=Store, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.store.name}: {self.name} в г. {self.city.name}, {self.city.country.name}'

    class Meta:
        verbose_name = "Склад"
        verbose_name_plural = "Склады"


class Stock(models.Model):
    """Остаток конкретного товара на конкретном складе"""
    item = models.ForeignKey(to=Item, on_delete=models.CASCADE)
    storage = models.ForeignKey(to=Storage, on_delete=models.CASCADE)
    amount = models.IntegerField()

    def __str__(self):
        return f'{self.storage.store.name}, {self.storage.name}: {self.item.name} {self.amount} {self.item.uom.name}'

    class Meta:
        verbose_name = "Остаток"
        verbose_name_plural = "Остатки"


class Enter(models.Model):
    """Оприходование"""
    item = models.ForeignKey(to=Item, on_delete=models.CASCADE)
    storage = models.ForeignKey(to=Storage, on_delete=models.CASCADE)
    amount = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    document_number = models.CharField(max_length=50, blank=True, null=True)
    supplier = models.CharField(max_length=200, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        stock = Stock.objects.filter(item=self.item, storage=self.storage)
        if stock:
            stock[0].amount += self.amount
            stock[0].save()
        else:
            Stock.objects.create(item=self.item, storage=self.storage, amount=self.amount)
        super(Enter, self).save(*args, **kwargs)

    def __str__(self):
        return f'Оприходование {self.item.name} - {self.amount} {self.item.uom.name}'

    class Meta:
        verbose_name = "Оприходование"
        verbose_name_plural = "Оприходования"


class WriteOff(models.Model):
    """Списание товаров"""
    item = models.ForeignKey(to=Item, on_delete=models.CASCADE)
    storage = models.ForeignKey(to=Storage, on_delete=models.CASCADE)
    amount = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    document_number = models.CharField(max_length=50, blank=True, null=True)
    reason = models.CharField(max_length=200, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        stock = Stock.objects.filter(item=self.item, storage=self.storage)
        if stock and stock[0].amount >= self.amount:
            stock[0].amount -= self.amount
            stock[0].save()
        else:
            raise ValueError("Недостаточно товара на складе для списания")
        super(WriteOff, self).save(*args, **kwargs)

    def __str__(self):
        return f'Списание {self.item.name} - {self.amount} {self.item.uom.name}'

    class Meta:
        verbose_name = "Списание"
        verbose_name_plural = "Списания"


class InventoryCheck(models.Model):
    """Инвентаризация склада"""
    storage = models.ForeignKey(to=Storage, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    document_number = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Черновик'),
        ('in_progress', 'В процессе'),
        ('completed', 'Завершена'),
        ('cancelled', 'Отменена')
    ], default='draft')

    def __str__(self):
        return f'Инвентаризация {self.storage.name} от {self.created_at.strftime("%d.%m.%Y")}'

    class Meta:
        verbose_name = "Инвентаризация"
        verbose_name_plural = "Инвентаризации"


class InventoryCheckItem(models.Model):
    """Позиция инвентаризации"""
    inventory_check = models.ForeignKey(to=InventoryCheck, on_delete=models.CASCADE)
    item = models.ForeignKey(to=Item, on_delete=models.CASCADE)
    expected_amount = models.IntegerField(help_text="Ожидаемое количество по учету")
    actual_amount = models.IntegerField(help_text="Фактическое количество при инвентаризации")
    difference = models.IntegerField(default=0, help_text="Разница (факт - учет)")
    notes = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        self.difference = self.actual_amount - self.expected_amount
        super(InventoryCheckItem, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.inventory_check} - {self.item.name}'

    class Meta:
        verbose_name = "Позиция инвентаризации"
        verbose_name_plural = "Позиции инвентаризации"
        verbose_name = "Инвентаризация"
        verbose_name_plural = "Инвентаризации"


class InventoryCheckItem(models.Model):
    """Позиция инвентаризации"""
    inventory_check = models.ForeignKey(to=InventoryCheck, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(to=Item, on_delete=models.CASCADE)
    expected_amount = models.IntegerField(default=0)  # Ожидаемое количество по системе
    actual_amount = models.IntegerField(default=0)    # Фактическое количество при подсчете
    difference = models.IntegerField(default=0)       # Разница (actual - expected)

    def save(self, *args, **kwargs):
        self.difference = self.actual_amount - self.expected_amount
        super(InventoryCheckItem, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.item.name}: ожид. {self.expected_amount}, факт. {self.actual_amount}'

    class Meta:
        verbose_name = "Позиция инвентаризации"
        verbose_name_plural = "Позиции инвентаризации"


class PaymentMethod(models.Model):
    name = models.CharField(max_length=120)
    icon = models.ImageField(upload_to='images/')
    description = models.TextField()

    class Meta:
        verbose_name = "Способ оплаты"
        verbose_name_plural = "Способы оплаты"


class StorePaymentMethod(models.Model):
    store = models.ForeignKey(to=Store, on_delete=models.CASCADE)
    payment_method = models.ForeignKey(to=PaymentMethod, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Способ оплаты магазина"
        verbose_name_plural = "Способы оплаты магазина"


class MoyskladIntegration(models.Model):
    store = models.OneToOneField(to=Store, on_delete=models.CASCADE)
    token = models.CharField(max_length=64)
    sync_status = models.BooleanField(default=False)
