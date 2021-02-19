from django import forms
from .models import Product, Material, Image


class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = [
            'name',
            'image',
        ]

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name',
            'description',
            'price',
            'is_active',
        ]

class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = [
            'image'
        ]
