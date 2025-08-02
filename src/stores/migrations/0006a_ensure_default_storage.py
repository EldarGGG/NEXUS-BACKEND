from django.db import migrations

def ensure_default_storage(apps, schema_editor):
    """
    Гарантированно заполняет поле default_storage для всех товаров.
    Создает дефолтный склад для магазинов без складов и связывает с ним товары.
    """
    Item = apps.get_model('stores', 'Item')
    Storage = apps.get_model('stores', 'Storage')
    Store = apps.get_model('stores', 'Store')
    
    # Словарь для хранения дефолтных складов по магазинам
    default_storages = {}
    
    # Для каждого товара без default_storage
    for item in Item.objects.filter(default_storage__isnull=True):
        # Если для этого магазина уже создали дефолтный склад, используем его
        if item.store_id in default_storages:
            item.default_storage = default_storages[item.store_id]
        else:
            # Попробуем найти существующий склад магазина
            storage = Storage.objects.filter(store=item.store).first()
            
            if not storage:
                # Если склада нет, создадим новый дефолтный склад
                try:
                    store = Store.objects.get(id=item.store_id)
                    storage = Storage.objects.create(
                        name='Основной склад',
                        description='Автоматически созданный основной склад',
                        store=store
                    )
                except Exception as e:
                    # В случае ошибки, пропустим этот товар
                    print(f"Ошибка при создании склада для магазина {item.store_id}: {e}")
                    continue
            
            # Сохраним склад в словарь для быстрого доступа
            default_storages[item.store_id] = storage
            item.default_storage = storage
        
        try:
            item.save()
        except Exception as e:
            print(f"Ошибка при сохранении товара {item.id}: {e}")


class Migration(migrations.Migration):

    dependencies = [
        ('stores', '0006_fill_default_storage'),
    ]

    operations = [
        migrations.RunPython(ensure_default_storage),
    ]
