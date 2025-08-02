from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from stores.models import Store

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_store(sender, instance, created, **kwargs):
    """
    Автоматически создает магазин для нового пользователя
    """
    if created:
        # Создаем магазин только если у пользователя его еще нет
        if not hasattr(instance, 'store_set') or not instance.store_set.exists():
            Store.objects.create(
                owner=instance,
                name=f"Магазин {instance.username}",
                description=f"Магазин пользователя {instance.get_full_name() or instance.username}",
                email=instance.email or f"{instance.username}@example.com",
                phone="",  # Можно будет заполнить позже в настройках
            )


@receiver(post_save, sender=User)
def save_user_store(sender, instance, **kwargs):
    """
    Сохраняет изменения в магазине при обновлении пользователя
    """
    if hasattr(instance, 'store_set') and instance.store_set.exists():
        store = instance.store_set.first()
        # Обновляем email магазина если изменился email пользователя
        if store.email != instance.email and instance.email:
            store.email = instance.email
            store.save()
