from django.db import models
from django.conf import settings

class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # 위시리스트 추가한 사용자
    festival = models.ForeignKey('festivals.Festival', on_delete=models.CASCADE)  # 위시리스트에 담은 축제
    notify = models.BooleanField(default=True)  # 알림 수신 여부 (True이면 축제 관련 알림 전송)
    added_date = models.DateTimeField(auto_now_add=True)  # 위시리스트에 추가된 시간

    class Meta:
        unique_together = [('user', 'festival')]  # 한 사용자당 동일 축제 하나만 위시리스트에 추가 가능

    def __str__(self):
        return f"{self.user.username} -> {self.festival.name}"
