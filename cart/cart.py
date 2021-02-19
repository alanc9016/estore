import datetime
from datetime import datetime as dt, timedelta, timezone
from json import JSONEncoder

from django.db.models import Sum
from django.db.models import FloatField, F
from . import models
from products.models import Image

CART_ID = 'CART-ID'


class ItemAlreadyExists(Exception):
    pass


class ItemDoesNotExist(Exception):
    pass


class Cart:
    def __init__(self, request):
        cart_id = request.session.get(CART_ID)
        if cart_id:
            cart = models.Cart.objects.filter(id=cart_id, checked_out=False).first()
            if cart is None:
                cart = self.new(request)
        else:
            cart = self.new(request)
        self.cart = cart

    def __iter__(self):
        for item in self.cart.item_set.all():
            yield item

    def new(self, request):
        carts = models.Cart.objects.all()
        for cart in carts:
            if dt.now(timezone.utc) - cart.creation_date > timedelta(1):
                cart.delete()
        cart = models.Cart.objects.create(creation_date=datetime.datetime.now(timezone.utc))
        request.session[CART_ID] = str(cart.id)
        return cart

    def add(self, product, unit_price, quantity=1):
        item = models.Item.objects.filter(cart=self.cart, product=product).first()
        if item:
            item.unit_price = unit_price
            item.quantity += int(quantity)
            q = item.quantity
            item.save()
            return q
        else:
            models.Item.objects.create(cart=self.cart, product=product, unit_price=unit_price, quantity=quantity)
            return 1


    def remove(self, product):
        item = models.Item.objects.filter(cart=self.cart, product=product).first()
        if item:
            if item.quantity == 1:
                item.delete()
            else:
                item.quantity -= 1
                item.save()
        # else:
        #     raise ItemDoesNotExist

    def update(self, product, quantity, unit_price=None):
        item = models.Item.objects.filter(cart=self.cart, product=product).first()
        if item:
            if quantity == 0:
                item.delete()
            else:
                item.unit_price = unit_price
                item.quantity = int(quantity)
                item.save()
        else:
            raise ItemDoesNotExist

    def count(self):
        return self.cart.item_set.all().aggregate(Sum('quantity')).get('quantity__sum', 0)

    def summary(self):
        return self.cart.item_set.all().aggregate(
            total=Sum(F('quantity') * F('unit_price'), output_field=FloatField())).get('total', 0)

    def clear(self):
        self.cart.item_set.all().delete()

    def is_empty(self):
        return self.count() == 0

    def cart_serializable(self):
        representation = {}
        for item in self.cart.item_set.all():
            item_id = str(item.object_id)
            if Image.objects.filter(product=item.product).exists():
                image = Image.objects.filter(product=item.product).first()
                image = image.image.url
            else:
                image = ''
            item_dict = {
                'name': item.product.name,
                'image': image,
                'description': item.product.description,
                'unit_price': item.unit_price,
                'total_price': item.total_price,
                'quantity': item.quantity,
            }
            representation[item_id] = item_dict
        return representation

    def cart_serializable_stripe(self):
        representation = {}

        for item in self.cart.item_set.all():
            item_id = str(item.object_id)
            item_dict = {
                'price': item.product.price_id,
                'quantity': item.quantity,
            }
            representation[item_id] = item_dict

        # if self.get_shipping_cost() == 15000:
        #     representation['shipping_rate'] = {
        #         'price': 'price_1HwuSpCqiKsYN6O7iVETMKDY',
        #         'quantity': 1,
        #     }
        # elif self.get_shipping_cost() == 20000:
        #     representation['shipping_rate'] = {
        #         'price': 'price_1HwuTDCqiKsYN6O7FeWyxNDj',
        #         'quantity': 1,
        #     }
        # elif self.get_shipping_cost() == 30000:
        #     representation['shipping_rate'] = {
        #         'price': 'price_1HwuThCqiKsYN6O7It50wbr1',
        #         'quantity': 1,
        #     }
        # else:
        #     representation['shipping_rate'] = {
        #         'price': 'price_1HwuUOCqiKsYN6O7KXWnqy6q',
        #         'quantity': 1,
        #     }
        return representation

    def get_shipping_cost(self):
        subtotal = self.summary()
        subtotal/= 100
        shipping_cost = 0
        if subtotal >= 1 and subtotal <= 999:
            shipping_cost = 15000
        elif subtotal > 999 and subtotal <= 1999:
            shipping_cost = 20000
        elif subtotal > 1999 and subtotal <= 2999:
            shipping_cost = 30000
        else:
            shipping_cost = 45000
        
        return shipping_cost
