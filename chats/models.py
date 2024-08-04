from django.db import models

from accounts.models import User

class Chat(models.Model):
  writer      = models.ForeignKey(User, on_delete=models.CASCADE) # 작성자

  content     = models.TextField()     # 채팅 텍스트
  created_at  = models.DateTimeField(auto_now_add=True) # 날짜 조회 할 때 사용