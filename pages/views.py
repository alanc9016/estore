from django.shortcuts import render
from django.http import HttpResponse

from products.models import Material


def home_view(request, *args, **kwargs):
    materials = Material.objects.all()
    return render(request, 'pages/home.html', {'materials': materials})


