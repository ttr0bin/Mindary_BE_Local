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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('mindary', main_page),
    path('mindary/<int:id>', chat_detail),   # chat 삭제 기능 - 필요없으면 나중에 뺍시다.
    path('mindary/records', record_mode),    # GET - 모아보기 / POST - 긴글 작성
    path('mindary/records/<int:id>', record_detail),    # 긴글 수정, 좋아요 기능
]
