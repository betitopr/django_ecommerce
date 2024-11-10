from django.urls import path

from . import views
app_name = 'store'  # This is the required app_name
urlpatterns = [
	#Leave as empty string for base url
	path('', views.store, name='store'),  # Cambia 'store/' a ''

	path('cart/', views.cart, name="cart"),
	path('checkout/', views.checkout, name="checkout"),

	path('update_item/', views.updateItem, name="update_item"),
	path('process_order/', views.processOrder, name="process_order"),
    path('products/', views.product_list, name='product_list'),
    path('create-customer/', views.create_customer, name='create_customer'),  # URL para crear el perfil
	path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),
    path('category/<int:id>/', views.category, name='category'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    path('apply-coupon/', views.apply_coupon, name='apply_coupon'),

]