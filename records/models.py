from django.db import models

from accounts.models import User

class Record(models.Model):
  writer      = models.ForeignKey(User, on_delete=models.CASCADE) # 작성자

  category    = models.CharField(max_length=30)
  title       = models.TextField()    # 제목
  content     = models.TextField()    # 본문
  created_at  = models.DateTimeField(auto_now_add=True) # 날짜 조회 할 때 사용
  edited_at   = models.DateTimeField(null=True, blank=True)  # 수정 시간
  liked       = models.BooleanField(default=False) # 작성자가 좋아요 하면 True