from django.urls import path
from .views import index_view
from . import views

urlpatterns = [
    path("", index_view, name="index"),
    path("register", views.register_view, name="register"),
    path("login", views.loginPague_view, name="login"),
    path("logout", views.logoutUser_view, name="logout"),
    path("add_item", views.add_item_view, name="add_item"),
    path("remove_item", views.remove_item_view, name="remove_item"),
    path("carrito", views.cart_view, name="carrito"),
    path("place_order", views.place_order_view, name="place_order"),
    path("show_order", views.show_order_view, name="show_order"),

]
