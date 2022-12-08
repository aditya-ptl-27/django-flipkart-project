from django.urls import path
from . import views
urlpatterns = [
    path('',views.index,name='index'),
    path('category/',views.category,name='category'),
  
    path('checkout/',views.checkout,name='checkout'),
    path('cart/',views.cart,name='cart'),
    path('confirmation/',views.confirmation,name='confirmation'),
    path('blog/',views.blog,name='blog'),
    path('single_blog/',views.single_blog,name='single_blog'),
    path('login/',views.login,name='login'),
    path('tracking/',views.tracking,name='tracking'),
    path('elements/',views.elements,name='elements'),
    path('contact/',views.contact,name='contact'),
    path('signup/',views.signup,name='signup'),
    path('logout/',views.logout,name='logout'),
    path('change_password/',views.change_password,name='change_password'),
    path('profile/',views.profile,name='profile'),
    path('seller_index/',views.seller_index,name='seller_index'),
    path('seller_change_password/',views.seller_change_password,name='seller_change_password'),
    path('seller_profile/',views.seller_profile,name='seller_profile'),
    path('seller_add_product/',views.seller_add_product,name='seller_add_product'),
    path('seller_view_product/',views.seller_view_product,name='seller_view_product'),
    # path('meet/',views.meet,name='meet'),
    path('seller_product_detail/<int:pk>/',views.seller_product_detail,name='seller_product_detail'),
    path('seller_product_edit/<int:pk>/',views.seller_product_edit,name='seller_product_edit'),
    path('seller_product_delete/<int:pk>/',views.seller_product_delete,name='seller_product_delete'),
    path('product_detail/<int:pk>/',views.product_detail,name='product_detail'),
    path('add_to_wishlist/<int:pk>/',views.add_to_wishlist,name='add_to_wishlist'),
    path('wishlist/',views.wishlist,name='wishlist'),
    path('remove_from_wishlist/<int:pk>/',views.remove_from_wishlist,name='remove_from_wishlist'),

    path('add_to_cart/<int:pk>/',views.add_to_cart,name='add_to_cart'),
    path('cart/',views.cart,name='cart'),
    path('remove_from_cart/<int:pk>/',views.remove_from_cart,name='remove_from_cart'),
    path('change_qty/<int:pk>/',views.change_qty,name='change_qty'),

    path('forgot_password/',views.forgot_password,name='forgot_password'),
    path('verify_otp/',views.verify_otp,name='verify_otp'),
    path('update_password/',views.update_password,name='update_password'),
    path('pay/',views.initiate_payment,name='pay'),
    path('callback/',views.callback,name='callback'),
    path('ajax/validate_email/',views.validate_email, name='validate_email'),
]