from django.urls import path, include
from .views import RegisterView, PasswordResetRequestView, PasswordResetConfirmView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import  create_order,order_success,create_item,item_list

urlpatterns = [
    # User registration endpoint
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),   
    path('accounts/', include('allauth.urls')), #included google auth
    path('password-reset/request/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('create/order/', create_order, name='create_order'),
    path('create/items/', create_item, name='create_item'),
    path('items/',  item_list, name='item_list'), 
    path('order_success/<int:temp_order_id>/', order_success, name='order_success'),
]
