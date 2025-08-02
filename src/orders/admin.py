from django.contrib import admin

from .models import Cart, CartItem, Order, OrderItem, Task, TaskCategory, TaskComment, TaskAttachment


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'store', 'status', 'total_price', 'created_at']
    list_filter = ['status', 'created_at', 'store']
    search_fields = ['order_number', 'user__email', 'store__name']
    readonly_fields = ['order_number', 'created_at', 'updated_at']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'item', 'amount', 'price_per_item', 'total_price']
    list_filter = ['order__status', 'item__store']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'priority', 'assigned_to', 'store', 'due_date', 'created_at']
    list_filter = ['status', 'priority', 'category', 'store', 'created_at']
    search_fields = ['title', 'description', 'assigned_to__email']
    readonly_fields = ['created_at', 'updated_at', 'completed_at']
    

@admin.register(TaskCategory)
class TaskCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'color']
    search_fields = ['name']


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ['task', 'author', 'created_at']
    list_filter = ['created_at', 'task__status']
    search_fields = ['content', 'author__email']


@admin.register(TaskAttachment)
class TaskAttachmentAdmin(admin.ModelAdmin):
    list_display = ['filename', 'task', 'uploaded_by', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['filename', 'task__title']


admin.site.register(Cart)
admin.site.register(CartItem)
