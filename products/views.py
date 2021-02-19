from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View

from .forms import ProductForm, MaterialForm, ImageForm
from django.forms import inlineformset_factory
from django.db.models import Max
from custom_storage import MediaStorage
from .models import Product, Material, Image
from django.db.models import Q
from cart.models import Item
import stripe


def product_view(request, material_id):
    material = get_object_or_404(Material, id=material_id)
    products = Product.objects.filter(material_id=material_id)

    if not request.user.is_superuser:
        products = products.filter(is_active=True)

    images = []
    prod = []
    for p in products:
        if Image.objects.filter(product=p).exists():
           images.append(Image.objects.filter(product=p).first())
        else:
            prod.append(p)

    paginator = Paginator(images, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'product/products.html', {'page_obj': page_obj, 'images': images, 'material': material, 'products': prod})

def create_material_view(request):
    if not request.user.is_superuser:
        return HttpResponse('Unauthorized', status=401)
    form = MaterialForm()
    if request.method == 'POST':
        form = MaterialForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            form = MaterialForm()
    context = {
        'form': form
    }
    return render(request, 'product/create_material.html', context)

def edit_material_view(request, material_id):
    if not request.user.is_superuser:
        return HttpResponse('Unauthorized', status=401)
    if request.method == 'POST':
        material = get_object_or_404(Material, id=material_id)
        form = MaterialForm(request.POST or None, instance=material)

        if form.is_valid():
            form.save()
            if request.FILES.get('image', None) is not None:
                material.image.delete()
                material.image = request.FILES['image']
                material.save()
    else:
        material = get_object_or_404(Material, id=material_id)
        return render(request, 'product/edit_material.html', {'material': material})

    return redirect('home')

def create_view(request, material_id):
    if not request.user.is_superuser:
        return HttpResponse('Unauthorized', status=401)
    material = get_object_or_404(Material, id=material_id)
    stripe.api_key = settings.STRIPE_SECRET_KEY

    form = ProductForm()
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)

            product = stripe.Product.create(
                name = instance.name,
                description= instance.description,
                active = False,
            )

            instance.id = product.id
            instance.material = material
            instance.save()

            price = stripe.Price.create(
                product= product.id,
                unit_amount=instance.price,
                currency='usd',
            )
            instance.price_id = price.id
            instance.save()
        else:
            print(form.errors)

            return redirect('product/create', material_id=material.id)

    return render(request, 'product/create.html', {'form': form, 'material':material})

def detail_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if not request.user.is_superuser:
        if not product.is_active:
            return HttpResponse('Unauthorized', status=401)

    images = Image.objects.filter(product_id=product_id)
    imgs = []
    for i in images:
        imgs.append(i.image.url)
    p_dict = {
        'name': product.name,
        'images': imgs,
        'description': product.description,
        'price': product.price,
    }

    if request.is_ajax():
        return JsonResponse({'product': p_dict}, status=200)

    return render(request, 'product/detail.html', {'product': product})

def product_images_view(request, product_id):
    if not request.user.is_superuser:
        return HttpResponse('Unauthorized', status=401)
    images = Image.objects.filter(product=product_id)

    return render(request, 'product/images.html', {'images':images})

def delete_image_view(request, image_id):
    if not request.user.is_superuser:
        return HttpResponse('Unauthorized', status=401)
    image = get_object_or_404(Image, id=image_id)
    product = image.product
    if request.method == "POST":
        image.delete()
        return redirect('home')

    return render(request, 'product/delete.html', {'object':image})

def edit_view(request, product_id):
    if not request.user.is_superuser:
        return HttpResponse('Unauthorized', status=401)
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        price = product.price
        form = ProductForm(request.POST or None, instance=product)
        stripe.api_key = settings.STRIPE_SECRET_KEY

        if form.is_valid():
            form.save()
            items = Item.objects.filter(object_id=product_id)
            items.update(unit_price=product.price)
            stripe.Product.modify(
                product.id,
                name = product.name,
                description = product.description,
                active = product.is_active,
            )
            if not product.is_active:
                Item.objects.filter(object_id=product.id).delete()
            if price != product.price:
                price = stripe.Price.create(
                    product = product.id,
                    unit_amount = product.price,
                    currency='usd',
                )
                product.price_id = price.id
                product.save()
    else:
        product = get_object_or_404(Product, id=product_id)
        return render(request, 'product/edit.html', {'product': product})

    return redirect('home')

def create_image_view(request, product_id):
    if not request.user.is_superuser:
        return HttpResponse('Unauthorized', status=401)
    product = get_object_or_404(Product, id=product_id)
    images = Image.objects.all()
    product_images = Image.objects.filter(product=product)
    form = ImageForm()
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        next_id = images.aggregate(Max('id'))['id__max'] + 1 if images else 1
        file_name = product.name+'_'+ str(next_id) + '.jpg'
        if form.is_valid():
            media_storage = MediaStorage()
            instance = form.save(commit=False)
            media_storage.save(file_name, instance.image)
            instance.product = product
            instance.image = file_name
            instance.save()
        else:
            print(form.errors)

            return redirect('product/create_image', product_id=product.id)
    return render(request, 'product/create_image.html', {'form': form, 'product': product})

def search_view(request):
    products = Product.objects.all()
    query = request.GET.get('q')

    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
            | Q(id__icontains=query)
        )
    if not request.user.is_superuser:
        products = products.filter(is_active=True)

    images = []
    prod = []
    for p in products:
        if Image.objects.filter(product=p).exists():
           images.append(Image.objects.filter(product=p).first())
        else:
            prod.append(p)

    paginator = Paginator(images, 8)
    print(paginator)
    page_number = request.GET.get('page')

    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, 'product/search.html', {'page_obj': page_obj, 'images': images, 'products': prod})

