from django import forms

from .models import *


class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ('name', 'description', 'logo', 'email', 'phone')
        widgets = {
            'owner': forms.HiddenInput()
        }


class IntegrationForm(forms.ModelForm):
    class Meta:
        model = Integration
        fields = ['name', 'description', 'image', 'status']


class SelfPickupPointForm(forms.ModelForm):
    class Meta:
        model = SelfPickupPoint
        fields = ['name', 'address']


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        exclude = ['status']
        widgets = {
            'owner': forms.HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.fields['subcategory'].empty_label = "Категория не выбрана"
        self.fields['uom'].empty_label = "Единица измерения не выбрана"


class ItemImageForm(forms.ModelForm):
    class Meta:
        model = ItemImage
        exclude = ['item']


class StorageForm(forms.ModelForm):
    class Meta:
        model = Storage
        fields = "__all__"
        widgets = {
            'store': forms.HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['city'].empty_label = "Город не выбран"
