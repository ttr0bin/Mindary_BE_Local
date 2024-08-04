from django.urls import path
from .views import *

urlpatterns = [
    path('wordcloud/get-wordcloud', get_wordcloud), 

    path('archive', archive), # archive
    path('archive/<int:id>', detail_archive), # archive 중 글 1개
]