from django.urls import path, include
from . import views
# from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    #User registration and token generation endpoints 
    path('', include('djoser.urls')),
    path('', include('djoser.urls.authtoken')),

    # group management
    path('groups/<str:group_name>/users', views.UserGroupManagement.as_view()),
    path('groups/<str:group_name>/users/<int:userId>', views.UserGroupManagement.as_view()),

    #MenuItemview
    path('menu-items/', views.MenuItemList.as_view()),
    path('menu-items/<int:pk>/', views.MenuItemDetail.as_view()),

    #Cart management endpoints
    path('cart/menu-items/', views.CartList.as_view()),

    #Order management endpoints
    path('orders/', views.OrderList.as_view()),
    path('orders/<int:pk>/', views.OrderDetail.as_view()),
]
