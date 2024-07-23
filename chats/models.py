from django.db import models

# Create your models here.
class Chat(models.Model):
  content = models.TextField()     # 채팅 텍스트
  created_at = models.DateTimeField(auto_now_add=True) # 날짜 조회 할 때 사용