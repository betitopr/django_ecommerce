from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
import json
import datetime
from .models import * 
from .utils import cookieCart, cartData, guestOrder
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages

# Vista para el inicio de sesión
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('store:store')  # Redirige a la tienda después de iniciar sesión
        else:
            # Si las credenciales son incorrectas
            return render(request, 'store/login.html', {'error': 'Invalid credentials'})
    
    return render(request, 'store/login.html')

# Vista para el cierre de sesión
def user_logout(request):
    logout(request)  # Cierra la sesión del usuario
    return redirect('store:login')  # Redirige correctamente a la vista de login

# Vista para el registro de un nuevo usuario
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        email = request.POST.get('email')

        # Verificar si las contraseñas coinciden
        if password != password2:
            return render(request, 'store/register.html', {'error': 'Passwords do not match'})

        # Verificar si el nombre de usuario ya existe
        if User.objects.filter(username=username).exists():
            return render(request, 'store/register.html', {'error': 'Username already exists'})

        # Crear el nuevo usuario
        user = User.objects.create_user(username=username, password=password, email=email)

        # Iniciar sesión automáticamente después del registro del usuario
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('store:create_customer')  # Redirige a la vista para crear el perfil de cliente

    return render(request, 'store/register.html')

# Vista para la página de la tienda
def store(request):
    # Obtener todas las categorías
    categories = Category.objects.all()

    # Obtener productos destacados, si tienes alguna lógica para definirlos
    featured_products = Product.objects.filter(is_featured=True)  # Suponiendo que tienes un campo is_featured

    # Obtener todos los productos
    products = Product.objects.all()  # Asegúrate de que esta línea esté presente para definir 'products'

    # Obtener los datos del carrito (si los tienes en utils)
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {
        'products': products,  # Ahora 'products' está definida
        'cartItems': cartItems,
        'categories': categories,
        'featured_products': featured_products,  # Pasa los productos destacados
    }

    return render(request, 'store/store.html', context)

# Vista para la categoría de productos
def category(request, id):
    category = get_object_or_404(Category, id=id)
    products = Product.objects.filter(category=category)
    return render(request, 'store/category.html', {'category': category, 'products': products})

# Vista para el detalle de un producto
def product_detail(request, id):
    product = Product.objects.get(id=id)  # Obtén el producto por ID
    return render(request, 'store/product_detail.html', {'product': product})

# Vista para el carrito de compras
def cart(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)

# Vista para el proceso de checkout
def checkout(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context)

# Vista para actualizar el carrito
def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action:', action)
    print('Product:', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)

# Vista para procesar un pedido
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )

    return JsonResponse('Payment submitted..', safe=False)

# Vista para la creación del perfil de cliente
def create_customer(request):
    if not request.user.is_authenticated:
        return redirect('store:login')  # Redirigir a la página de login si no está autenticado

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')

        # Verificar si el cliente ya existe
        if Customer.objects.filter(user=request.user).exists():
            return render(request, 'store/create_customer.html', {'error': 'Customer profile already exists.'})

        # Crear el objeto Customer
        customer = Customer.objects.create(
            user=request.user,  # Relacionamos al usuario actual
            name=name,
            email=email
        )

        return redirect('store:store')  # Redirigir al usuario a la tienda después de crear su perfil de cliente.

    return render(request, 'store/create_customer.html')

# Vista para listar todos los productos
def product_list(request):
    products = Product.objects.all()  # Obtiene todos los productos de la base de datos
    return render(request, 'store/product_list.html', {'products': products})
