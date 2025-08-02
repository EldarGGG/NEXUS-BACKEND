from django.db import migrations

def set_default_storage(apps, schema_editor):
    """
    Заполняет поле default_storage для существующих товаров,
    используя первый склад из связанных записей Stock или
    первый доступный склад магазина, если Stock нет
    """
    Item = apps.get_model('stores', 'Item')
    Stock = apps.get_model('stores', 'Stock')
    Storage = apps.get_model('stores', 'Storage')
    
    # Для каждого товара без default_storage
    for item in Item.objects.filter(default_storage__isnull=True):
        # Попробуем найти существующие записи Stock для этого товара
        stock = Stock.objects.filter(item=item).first()
        
        if stock:
            # Если есть запись Stock, используем склад из неё
            item.default_storage = stock.storage
        else:
            # Иначе берём первый доступный склад магазина
            storage = Storage.objects.filter(store=item.store).first()
            if storage:
                item.default_storage = storage
            # Если склад не найден, товар останется с null (будет обработано позже)
        
        item.save()


class Migration(migrations.Migration):

    dependencies = [
        ('stores', '0005_item_default_storage'),
    ]

    operations = [
        migrations.RunPython(set_default_storage),
    ]
