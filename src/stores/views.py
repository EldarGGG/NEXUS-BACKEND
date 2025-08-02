from decimal import Decimal
from base64 import b64encode

import requests
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse

from .forms import *
from .models import *
from .services import *


@login_required(login_url='/login/')
def create_store(request, back_store_id):
    if request.method == 'POST':
        form = StoreForm(request.POST, request.FILES)
        if form.is_valid():
            store = form.save(commit=False)
            store.owner = request.user
            store.save()
            return redirect('home')
        else:
            print(form.errors)
    else:
        form = StoreForm()
    return render(request, 'create-store.html', {
        'form': form,
        'back_store_id': back_store_id
    })


@login_required(login_url='/login/')
def root(request):
    user = request.user
    user_stores = Store.objects.filter(owner=user)
    if user_stores:
        return redirect('home_store', store_id=user_stores[0].pk)
    return redirect('create_store')


@login_required(login_url='/login/')
def home_store(request, store_id):
    stores = Store.objects.filter(owner=request.user)

    context = {
        "stores": stores,
    }
    return render(request, 'home.html', context=context)


@login_required(login_url='/login/')
def store_integrations(request, store_id):
    stores = Store.objects.filter(owner=request.user)
    store = Store.objects.get(id=store_id)
    connected_integrations = Integration.objects.filter(integrationstore__store=store)
    available_integrations = Integration.objects.filter(status=True).exclude(integrationstore__store=store)
    unavailable_integrations = Integration.objects.filter(status=False)

    context = {
        "stores": stores,
        "connected_integrations": connected_integrations,
        "available_integrations": available_integrations,
        "unavailable_integrations": unavailable_integrations
    }
    return render(request, 'store-integrations.html', context=context)


@login_required(login_url='/login/')
def store_settings(request, store_id):
    stores = Store.objects.filter(owner=request.user)
    store = Store.objects.get(id=store_id)
    self_pickup_points = SelfPickupPoint.objects.filter(store=store)

    q = StorePaymentMethod.objects.filter(store__id=store_id).values('payment_method')
    available_payment_methods = PaymentMethod.objects.all().exclude(pk__in=q)
    connected_payment_methods = StorePaymentMethod.objects.filter(store__id=store_id)

    context = {
        "stores": stores,
        "store": store,
        "store_form": StoreForm,
        "pickup_point_form": SelfPickupPointForm,
        'self_pickup_points': self_pickup_points,
        "connected_payment_methods": connected_payment_methods,
        "available_payment_methods": available_payment_methods,
    }
    return render(request, "store-settings.html", context=context)


@login_required(login_url='/login/')
def store_items(request, store_id):
    stores = Store.objects.filter(owner=request.user)
    store = Store.objects.get(id=store_id)
    items = Item.objects.filter(store=store)

    context = {
        "stores": stores,
        "item_form": ItemForm,
        "items": items
    }
    return render(request, "store-items.html", context=context)


@login_required(login_url='/login/')
def store_params(request, store_id):
    stores = Store.objects.filter(owner=request.user)
    store = Store.objects.get(id=store_id)
    storages = Storage.objects.filter(store=store)

    context = {
        "stores": stores,
        "storages": storages,
        "storage_form": StorageForm,
    }
    return render(request, "store-params.html", context=context)


@login_required(login_url='/login/')
def item(request, store_id, item_id):
    item = Item.objects.get(pk=item_id)
    item_images = ItemImage.objects.filter(item=item)
    stocks = Stock.objects.filter(item=item).select_related('storage')
    context = {
        'item': item,
        'stocks': stocks,
        'item_images': item_images,
        'item_image_form': ItemImageForm
    }
    return render(request, "item.html", context=context)


@login_required(login_url='/login/')
def moysklad(request, store_id):
    integration = MoyskladIntegration.objects.filter(store_id=store_id)
    if not integration:
        integration_status = False
        token = None
    else:
        integration_status = True
        token = integration[0].token

    context = {
        "integration_status": integration_status,
        "token": token
    }
    return render(request, "moysklad.html", context=context)


def get_moysklad_token(request, store_id):
    login = request.POST.get('login')
    password = request.POST.get('password')
    credentials = b64encode(f"{login}:{password}".encode(encoding="utf-8")).decode("utf-8")
    headers = {
        "Authorization": "Basic " + credentials,
        "Accept-Encoding": "gzip"
    }
    response = requests.post(
        url='https://api.moysklad.ru/api/remap/1.2/security/token',
        headers=headers
    )
    token = response.json().get("access_token")
    context = {}
    if token:
        MoyskladIntegration.objects.create(store_id=store_id, token=token)
        context['integration_status'] = True
        context['token'] = token
        context['message'] = 'Успешно подключено'
    else:
        context['integration_status'] = False
        context['message'] = 'Произошла ошибка'

    return render(request, 'partials/moysklad-integration-status.html', context=context)


def create_pickup_point(request, store_id):
    store = Store.objects.get(id=store_id)
    SelfPickupPoint.objects.create(
        name=request.POST.get('name'),
        address=request.POST.get('address'),
        store=store
    )
    self_pickup_points = SelfPickupPoint.objects.filter(store=store)
    context = {
        'self_pickup_points': self_pickup_points
    }
    return render(request, 'partials/self-pickup-points-list.html', context=context)


def create_item(request, store_id):
    store = Store.objects.get(pk=store_id)
    uom = Uom.objects.get(pk=request.POST.get('uom'))
    Item.objects.create(
        name=request.POST.get('name'),
        store=store,
        description=request.POST.get('description'),
        status=True,  # request.POST.get('status')
        uom=uom,
        default_price=Decimal(request.POST.get('default_price')),
        preview=request.FILES['preview'],
    )

    items = Item.objects.filter(store=store)
    context = {
        'items': items
    }
    return render(request, 'partials/item-list.html', context=context)


def create_item_image(request, store_id, item_id):
    item = Item.objects.get(id=item_id)
    ItemImage.objects.create(
        item=item,
        description=request.POST.get('description'),
        image=request.FILES['image'],
    )
    item_images = ItemImage.objects.filter(item=item)
    context = {
        'item_images': item_images
    }
    return render(request, 'partials/item-image-list.html', context=context)


def create_storage(request, store_id):
    store = Store.objects.get(pk=store_id)
    city = City.objects.get(pk=request.POST.get('city'))
    Storage.objects.create(
        name=request.POST.get('name'),
        city=city,
        address=request.POST.get('address'),
        store=store
    )
    storages = Storage.objects.filter(store=store)
    context = {
        'storages': storages,
        "message": "склад успешно создан"
    }
    return render(request, 'partials/storage-list.html', context=context)


def create_connected_payment_method(request, store_id, payment_method_id):
    store = Store.objects.get(pk=store_id)
    payment_method = PaymentMethod.objects.get(pk=payment_method_id)

    StorePaymentMethod.objects.create(store=store, payment_method=payment_method)

    q = StorePaymentMethod.objects.filter(store__id=store_id).values('payment_method')
    available_payment_methods = PaymentMethod.objects.all().exclude(pk__in=q)
    connected_payment_methods = StorePaymentMethod.objects.filter(store__id=store_id)

    context = {
        "store": store,
        "connected_payment_methods": connected_payment_methods,
        "available_payment_methods": available_payment_methods,
    }

    return render(request, 'partials/payment-methods-list.html', context=context)


def delete_connected_payment_method(request, store_id, payment_method_id):
    store = Store.objects.get(pk=store_id)
    payment_method = PaymentMethod.objects.get(pk=payment_method_id)
    StorePaymentMethod.objects.get(store=store, payment_method=payment_method).delete()

    q = StorePaymentMethod.objects.filter(store__id=store_id).values('payment_method')
    available_payment_methods = PaymentMethod.objects.all().exclude(pk__in=q)
    connected_payment_methods = StorePaymentMethod.objects.filter(store__id=store_id)

    context = {
        "store": store,
        "connected_payment_methods": connected_payment_methods,
        "available_payment_methods": available_payment_methods,
    }

    return render(request, 'partials/payment-methods-list.html', context=context)


def delete_pickup_point(request, point_id):
    point = SelfPickupPoint.objects.get(id=point_id)
    store = point.store
    point.delete()
    self_pickup_points = SelfPickupPoint.objects.filter(store=store)
    context = {
        'self_pickup_points': self_pickup_points
    }
    return render(request, 'partials/self-pickup-points-list.html', context=context)


def delete_item(request, item_id):
    item = Item.objects.get(id=item_id)
    store = item.store
    item.delete()
    items = Item.objects.filter(store=store)
    context = {
        'items': items
    }
    return render(request, 'partials/item-list.html', context=context)


def delete_storage(request, storage_id):
    storage = Storage.objects.get(id=storage_id)
    store = storage.store

    stock = Stock.objects.filter(storage=storage)
    if stock:
        context = {
            "storages": Storage.objects.filter(store=store),
            "message": f"Отвяжите все остатки ({len(stock)})"
        }
        return render(request, 'partials/storage-list.html', context=context)

    storage.delete()

    context = {
        "storages": Storage.objects.filter(store=store),
        "message": f"Склад успешно удален"
    }
    return render(request, 'partials/storage-list.html', context=context)


def check_form_field(request, field_name):
    """
    Проверка доступности уникальных полей
    """
    print(request.POST)
    status = Store.objects.filter(**{field_name: request.POST[field_name]}).exists()
    if not status:
        return HttpResponse("""
    <div style="background-color: green;width: 200px;">
        yes
    </div>
    """)
    else:
        return HttpResponse("""
            <div style="background-color: red; width: 200px;">
                no
            </div>
            """)

# def delete_instance(request, instance_name, instance_id):
#    instances = {
#        "categories": Category,
#        "storage": Storage
#    }
#    inctance = instances[instance_name].objects.get(pk=instance_id)
#    inctance.delete()
