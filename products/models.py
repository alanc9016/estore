from django.db import models
from django.urls import reverse

# Create your models here.


class Material(models.Model):
    name = models.CharField(max_length=35)
    image = models.ImageField()

    def delete(self, *args, **kwargs):
        self.image.delete()
        super().delete(*args, **kwargs)
    
    def __str__(self):
        return self.name

class Product(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    name = models.CharField(max_length=35)
    description = models.TextField()
    price = models.IntegerField()
    price_id = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Image(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/')

    def delete(self, *args, **kwargs):
        self.image.delete()
        super().delete(*args, **kwargs)

