# from io import BytesIO
# import tempfile

import requests
# from PIL import Image
# from django.core.files.base import ContentFile

from .models import Item, Group, Uom


def get_entity_from_moysklad(token: str, entity: str) -> dict:
    headers = {
        "Authorization": "Bearer " + token
    }

    response = requests.get(
        url="https://api.moysklad.ru/api/remap/1.2/entity/" + entity,
        headers=headers
    )

    return response.json()


def sync_groups(token, store_id):
    res = get_entity_from_moysklad(token, 'productfolder')
    for group in res['rows']:

        is_root = False if group.get('productFolder') else True
        if not is_root:
            parent_external_id = group['productFolder']['meta']['uuidHref'].split('?id=')[1]
        else:
            parent_external_id = None

        Group.objects.create(
            store_id=store_id,
            name=group['name'],
            description=group.get('description'),
            external_id=group['id'],
            is_root=is_root,
            parent_external_id=parent_external_id
        )

    orphans = Group.objects.filter(is_root=False)

    for group in orphans:
        parent = Group.objects.filter(external_id=group.parent_external_id)

        if parent:
            group.parent = parent[0]
            group.save()


def sync_items(token, store_id):
    res = get_entity_from_moysklad(token, 'product')

    for item in res['rows']:
        group = None
        preview = None
        price = 0
        uom = None

        if item.get('productFolder'):
            try:
                group_external_id = item['productFolder']['meta']['href'].split('productfolder/')[1]
            except (IndexError, KeyError):
                group_external_id = None

            if group_external_id:
                group_set = Group.objects.filter(external_id=group_external_id)
                if group_set:
                    group = group_set[0]
                    print('group found')
                else:
                    group = None
                    print('group not found, no in db')

        if item.get('salePrices'):
            try:
                price = int(item['salePrices'][0]['value'])
            except IndexError:
                price = 0

        if item.get('uom'):
            uom_external_id = item['uom']['meta']['href'].split('uom/')[-1]
            uom = Uom.objects.filter(external_id=uom_external_id)
            if uom:
                uom = uom[0]

        '''if item.get('images'):
            try:
                images_meta_prefix = item['images']['meta']['href'].split('entity/')[1]
            except (IndexError, KeyError):
                images_meta_prefix = None
                print('image not found in item')

            if images_meta_prefix:
                try:
                    img_url = get_entity_from_moysklad(
                        token=token,
                        entity=images_meta_prefix
                    )['rows'][0]['meta']['downloadHref']
                except (IndexError, KeyError):
                    img_url = None
                    print('download link not found')

                if img_url:
                    preview_response = requests.get(img_url, stream=True)
                    if preview_response.status_code != requests.codes.ok:
                        lf = tempfile.NamedTemporaryFile()
                        for block in preview_response.iter_content(1024 * 8):
                            if not block:
                                break
                            lf.write(block)

                    else:
                        print('q')'''

        Item.objects.create(
            store_id=store_id,
            group=group,
            name=item['name'],
            preview=preview,
            default_price=price,
            uom=uom
        )
