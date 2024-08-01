"""
URL configuration for mindary project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from chats.views import main_page, chat_detail
from records.views import record_mode, record_detail
#from acccounts.views import send_verification_code, verify_code, register_user, login, logout, reset_password

urlpatterns = [
    path('admin/', admin.site.urls),
    path('mindary', main_page),
    path('mindary/<int:id>', chat_detail),   # chat 삭제 기능 - 필요없으면 나중에 뺍시다.
    path('mindary/records', record_mode),    # GET - 모아보기 / POST - 긴글 작성
    path('mindary/records/<int:id>', record_detail),    # 긴글 수정, 좋아요 기능

    # 일반 로그인 uri
    # path('mindary/accounts/original/login', login, name='original_login'),
    # path('mindary/accounts/original/logout', logout, name='original_logout'),
    # path('mindary/accounts/original/send-code', send_verification_code, name='send_code'),
    # path('mindary/accounts/original/verify-code', verify_code, name='verify_code'),
    # path('mindary/accounts/original/register', register_user, name='register_user'),
    # path('mindary/accounts/original/reset_password/', reset_password, name='reset_password'),

]
