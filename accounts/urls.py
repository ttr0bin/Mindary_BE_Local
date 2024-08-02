from django.urls import path
from .views import *

urlpatterns = [
    # Original_Login

    # Kakao_Login
    path('kakao/login/', kakao_login),
    path('kakao/register/', kakao_register),
    path('kakao/logout/', kakao_logout),
    path('kakao/verify/', verify),
]