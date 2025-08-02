from django.db import models
from django.utils import timezone

from users.models import CustomUser
from stores.models import Item, SelfPickupPoint, Store


class Cart(models.Model):
    user = models.OneToOneField(to=CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return f"Cart of user {self.user.email}"

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"


class CartItem(models.Model):
    cart = models.ForeignKey(to=Cart, on_delete=models.CASCADE)
    item = models.ForeignKey(to=Item, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.item.name}, {self.amount} {self.item.uom.name}"

    class Meta:
        verbose_name = "Товар корзины"
        verbose_name_plural = "Товары корзины"


class PaymentMethod(models.Model):
    name = models.CharField(max_length=120)


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('confirmed', 'Подтвержден'),
        ('processing', 'В обработке'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменен'),
        ('returned', 'Возвращен'),
    ]
    
    user = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE)
    store = models.ForeignKey(to=Store, on_delete=models.CASCADE, null=True, blank=True)
    self_pickup_point = models.ForeignKey(to=SelfPickupPoint, null=True, on_delete=models.SET_NULL)
    payment_method = models.ForeignKey(to=PaymentMethod, on_delete=models.CASCADE, null=True)
    comment = models.TextField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Дополнительные поля для отслеживания
    order_number = models.CharField(max_length=50, unique=True, blank=True)
    delivery_address = models.TextField(blank=True)
    delivery_date = models.DateTimeField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            # Генерируем уникальный номер заказа
            import uuid
            self.order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Заказ {self.order_number} - {self.user.email}"
    
    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created_at']


class OrderItem(models.Model):
    order = models.ForeignKey(to=Order, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(to=Item, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()
    price_per_item = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    
    def save(self, *args, **kwargs):
        if not self.price_per_item:
            self.price_per_item = self.item.default_price
        self.total_price = self.price_per_item * self.amount
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.item.name} x{self.amount} - {self.order.order_number}"
    
    class Meta:
        verbose_name = "Товар заказа"
        verbose_name_plural = "Товары заказа"


# Task Models
class TaskCategory(models.Model):
    """Категории задач"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#3B82F6')  # hex color
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Категория задач"
        verbose_name_plural = "Категории задач"


class Task(models.Model):
    """Модель задач для продавца"""
    PRIORITY_CHOICES = [
        ('low', 'Низкий'),
        ('medium', 'Средний'),
        ('high', 'Высокий'),
        ('urgent', 'Срочный'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('in_progress', 'В работе'),
        ('completed', 'Завершена'),
        ('cancelled', 'Отменена'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(TaskCategory, on_delete=models.SET_NULL, null=True, blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    
    # Связи
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='assigned_tasks')
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_tasks')
    
    # Временные метки
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Дополнительные поля
    estimated_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    actual_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"
    
    def save(self, *args, **kwargs):
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
        elif self.status != 'completed':
            self.completed_at = None
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
        ordering = ['-created_at']


class TaskComment(models.Model):
    """Комментарии к задачам"""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Комментарий к {self.task.title}"
    
    class Meta:
        verbose_name = "Комментарий к задаче"
        verbose_name_plural = "Комментарии к задачам"
        ordering = ['created_at']


class TaskAttachment(models.Model):
    """Вложения к задачам"""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='task_attachments/')
    filename = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.filename} - {self.task.title}"
    
    class Meta:
        verbose_name = "Вложение к задаче"
        verbose_name_plural = "Вложения к задачам"


class Counterparty(models.Model):
    """Модель контрагентов (клиенты, поставщики, партнеры)"""
    TYPE_CHOICES = [
        ('customer', 'Клиент'),
        ('supplier', 'Поставщик'),
        ('partner', 'Партнер'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Активный'),
        ('inactive', 'Неактивный'),
        ('blocked', 'Заблокирован'),
    ]
    
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='customer')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    
    # Связи
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    
    # Временные метки
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"
    
    @property
    def total_orders(self):
        """Количество заказов от этого контрагента"""
        # Пока возвращаем 0, можно будет добавить подсчет заказов
        return 0
    
    @property
    def total_spent(self):
        """Общая сумма потраченная контрагентом"""
        # Пока возвращаем 0, можно будет добавить подсчет суммы
        return "0.00"
    
    @property
    def last_order_date(self):
        """Дата последнего заказа"""
        # Пока возвращаем None, можно будет добавить поиск последнего заказа
        return None
    
    class Meta:
        verbose_name = "Контрагент"
        verbose_name_plural = "Контрагенты"
        ordering = ['-created_at']
