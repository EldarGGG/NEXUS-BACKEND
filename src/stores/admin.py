from django.contrib import admin
from .models import *
from .forms import IntegrationForm

admin.site.register(Uom)
admin.site.register(Currency)
admin.site.register(CounterpartyMember)
admin.site.register(CounterpartyGroup)
admin.site.register(Country)
admin.site.register(City)
admin.site.register(Storage)
admin.site.register(Stock)
admin.site.register(Enter)
admin.site.register(SelfPickupPoint)
admin.site.register(ItemImage)
admin.site.register(PaymentMethod)
admin.site.register(StorePaymentMethod)
admin.site.register(MoyskladIntegration)
admin.site.register(Group)


class StoreAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        if not obj.owner_id:
            obj.owner = request.user
        super().save_model(request, obj, form, change)


class IntegrationAdmin(admin.ModelAdmin):
    form = IntegrationForm
    list_display = ['name', 'status']


class IntegrationStoreAdmin(admin.ModelAdmin):
    list_display = ['store', 'integration']


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['store', 'name']


class ItemAdmin(admin.ModelAdmin):
    list_display = ['store', 'name', 'preview']


admin.site.register(Store, StoreAdmin)
admin.site.register(Integration, IntegrationAdmin)
admin.site.register(IntegrationStore, IntegrationStoreAdmin)
admin.site.register(Item, ItemAdmin)
