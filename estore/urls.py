"""estore URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from cart.views import (
        add_to_cart, 
        remove_from_cart, 
        get_cart, 
        stripe_config, 
        create_checkout_session, 
        success_view
)

from pages.views import home_view

urlpatterns = [
    path('products/', include('products.urls')),
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('cart/', get_cart, name='cart'),
    path('add_cart/<str:product_id>', add_to_cart, name='add_cart'),
    path('remove_from_cart/<str:product_id>', remove_from_cart, name='remove_from_cart'),
    path('config/', stripe_config),
    path('create_checkout_session/', create_checkout_session),
    path('success/', success_view),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
