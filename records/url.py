from django.urls import path
from .views import *

urlpatterns = [
    path('mindary/records', record_mode),    # GET - 모아보기 / POST - 긴 글 작성
    path('mindary/records/<int:id>', record_detail),    # 긴 글 수정, 좋아요 기능
]