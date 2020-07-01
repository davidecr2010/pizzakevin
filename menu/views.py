import smtplib
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core import serializers

from .models import (Pizza,Topping,Sub,Pasta,Salad,Dinner_Platter,Order,Cart,Extra,)



@login_required(login_url='login')
def index_view(request):
    """ Redireccionar a la página de inicio si el usuario ha iniciado sesión o bien a la página de inicio de sesión"""

    # segúrese de que el usuario haya iniciado sesión
    if not request.user.is_authenticated:
        return render(request, "orders/login.html", {"message": None})

    context = {
        "user": request.user,
        "pizzas": Pizza.objects.all(),
        "toppings": Topping.objects.values("name"),
        "subs": Sub.objects.all(),
        "extras": Extra.objects.all(),
        "pastas": Pasta.objects.all(),
        "salads": Salad.objects.all(),
        "dinner_platters": Dinner_Platter.objects.all(),
    }

    # Special Pizza
    special = "Pepperoni, Mushrooms, Ham, Cheese"
    context["special"] = special

    # Asegúrese de que se inicia el pedido, si no, inicie
    try:
        order = Order.objects.get(user=request.user, status="Initiated")
    except:
        order = Order(user=request.user)
        order.save()

    cart = Cart.objects.filter(user=request.user, order_id=order.pk)
    count = 0
    for item in cart:
        count += 1
    context["count"] = count
    # Render index.html page
    return render(request, "menu/index.html", context)



def register_view(request):
    """ Registrar usuario"""

    # El usuario alcanzó la ruta a través de POST (al enviar un formulario a través de POST)
    if request.method == "POST":
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        email = request.POST["email"]
        username = request.POST["username"]
        password = request.POST["password"]

        # Asegúrese de que el correo electrónico sea único
        user = User.objects.filter(email=email)
        if len(user) != 0:
            return render(request, "menu/register.html", {"message": "E-mail ya esta en uso!"})

        #  Asegúrese de que el username sea único
        user = User.objects.filter(username=username)
        if len(user) != 0:
            return render(request, "menu/register.html", {"message": "Username ya esta en uso!"})
        # Agregar usuario a la base de datos y guardarlo
        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=username,
            password=password,
        )
        user.save()

        return render(request, "menu/login.html", {"message": "Cuenta creada!"})
    # El usuario alcanzó la ruta a través de GET (como haciendo clic en un enlace o mediante redireccionamiento)
    else:
        return render(request, "menu/register.html")




def loginPague_view(request):
    """ Iniciar sesión de usuario """

    #Si el usuario ya existe, redireccionarlo al index
    if request.user.is_authenticated:
        return redirect('index')

    else:
        # El usuario alcanzó la ruta a través de POST (al enviar un formulario a través de POST)
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('index')

            else:
                messages.info(request, "Nombre de usuario o contraseña incorrecta")


        context = {}
        return render(request, 'menu/login.html', context)



def logoutUser_view(request):
    logout(request)
    return redirect('login')



#################################################################################

def add_item_view(request):
    """ Artículo de revisión """

    # Obtener campos de formulario
    name = request.POST["name"]
    item_price = float(request.POST["item_price"])
    size = request.POST["size"]
    # obtener ingredientes especiales de pizza
    try:
        special = request.POST["special"]
    except:
        special = ""
    # Generar nombre de extras
    extras = special
    # Asegúrese de que se hayan seleccionado ingredientes adicionales para pizzas / sandwiches
    try:
        extra1 = request.POST["extra1"]
    except:
        extra1 = ""
    try:
        extra2 = request.POST["extra2"]
    except:
        extra2 = ""
    try:
        extra3 = request.POST["extra3"]
    except:
        extra3 = ""
    try:
        extra4 = request.POST["extra4"]
    except:
        extra4 = ""

    # Generar nombre de elementos adicionales
    if len(extra1) != 0:
        extras += f"{extra1},"
    if len(extra2) != 0:
        extras += f"{extra2},"
    if len(extra3) != 0:
        extras += f"{extra3},"
    if len(extra4) != 0:
        extras += f"{extra4}"
    length = len(extras)

    try:
        if extras[length - 1] == ",":
            extras = extras[:-1]
    except:
        extras = ""
    extras = extras.replace(",", ", ")

    # Obtenga un precio adicional para los subs
    try:
        price1 = float(request.POST["price1"])
    except:
        price1 = 0.00
    try:
        price2 = float(request.POST["price2"])
    except:
        price2 = 0.00
    try:
        price3 = float(request.POST["price3"])
    except:
        price3 = 0.00
    try:
        price4 = float(request.POST["price4"])
    except:
        price4 = 0.00

    # Calcular precio extra total
    extra_price = price1 + price2 + price3 + price4

    # Agregar precio adicional al precio del artículo
    item_price += extra_price

    # Generar nombre del artículo del carrito
    cart_item = name
    if len(size) != 0:
        cart_item += f" ({size})"

    # Iniciar sesión usuario
    user = request.user

    # Obtenga la última orden iniciada
    order = Order.objects.get(user=user, status="Initiated")

    # Obtener ID de pedido
    order_id = order.id

    # Agregue el artículo en el carrito y guárdelo
    cart = Cart(
        user=user,
        order_id=order_id,
        cart_item=cart_item,
        extras=extras,
        item_price=item_price,
    )
    cart.save()

    # Incremento total del pedido con precio del artículo
    order.order_total = float(order.order_total) + item_price
    order.save()

    # Redirigir al usuario para indexar con un mensaje
    messages.success(request, "Artículo agregado!")
    return HttpResponseRedirect(reverse("index"))


def remove_item_view(request):
    """ Eliminacion de articulo"""

    item_id = request.POST["item_id"]
    item_price = request.POST["item_price"]

    user = request.user

    # Eliminar artículo del carrito
    cart = Cart.objects.filter(id=item_id).delete()

    # Disminuya el total del pedido con el precio del artículo
    order = Order.objects.get(user=user, status="Initiated")
    order.order_total = float(order.order_total) - float(item_price)
    order.save()


    messages.success(request, "Artículo eliminado!")
    return HttpResponseRedirect(reverse("carrito"))


def cart_view(request):
    """ Muestra el carrito y elimina artículos del carrito """


    # Obtener orden inicializada
    order = Order.objects.get(user=request.user, status="Initiated")

    # Obtén artículos del carrito
    cart = Cart.objects.filter(user=request.user, order_id=order.pk)

    # Contar artículos del carrito
    count = 0
    for item in cart:
        count += 1

    context = {
        "cart": cart,
        "count": count,
        "order_total": order.order_total,
        "order_id": order.id,
    }

    return render(request, "menu/cart.html", context)


def place_order_view(request):
    """ Realiza y completa un pedido """

    # Obtener ID de pedido
    order_id = request.POST["order_id"]

    # Obtener objeto de pedido del usuario
    order = Order.objects.get(user=request.user, status="Initiated")

    # Obtén artículos
    cart = Cart.objects.filter(user=request.user, order_id=order.pk).all()

    # Cambie el estado del pedido a completado y guárdelo
    order.status = "Completado"
    order.save()

    


    message = f"""
    Su pedido ha sido realizado con éxito!

     Usted ordeno:
        """
    for item in cart:
        message += f"""{item.cart_item}: ${item.item_price}
        """
        if item.extras != "":
            message += f"""({item.extras})
        """
        message += """
        """
    message += f"""
    El total de su orden: ${order.order_total}

    
    Gracias por visitarnos! ¡Esperamos que tengas un buen día!
    """


    messages.success(request, "Order has been placed!")
    return HttpResponseRedirect(reverse("index"))


def show_order_view(request):
    """ Muestra una lista de pedidos para el administrador """

    # Obtenga pedidos y artículos de carrito para cada pedido
    context = {
        "orders": Order.objects.all().filter(status="Completed"),
        "cart": Cart.objects.all(),
    }

    # Cuente los artículos del carrito y agréguelos al contexto
    order = Order.objects.get(user=request.user, status="Initiated")
    cart = Cart.objects.filter(user=request.user, order_id=order.pk)
    count = 0
    for item in cart:
        count += 1
    context["count"] = count


    return render(request, "menu/orders.html", context)