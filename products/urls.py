from django.urls import path

from .views import (
        create_view, 
        create_material_view, 
        edit_material_view, 
        detail_view, 
        edit_view, 
        search_view, 
        product_view, 
        create_image_view,
        product_images_view,
        delete_image_view,
)

urlpatterns = [
    path('create_material/', create_material_view, name='create_material'),
    path('edit_material/<int:material_id>', edit_material_view, name='edit_material'),
    path('<int:material_id>', product_view, name='products'),
    path('create/<int:material_id>', create_view, name='create'),
    path('detail/<str:product_id>', detail_view, name='detail'),
    path('delete_image/<int:image_id>', delete_image_view, name='delete_image'),
    path('edit/<str:product_id>', edit_view, name='edit'),
    path('search/', search_view, name='search'),
    path('create_image/<str:product_id>', create_image_view, name='create_image'),
    path('images/<str:product_id>', product_images_view, name='images'),
]
