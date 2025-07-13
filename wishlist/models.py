from django.db import models
from django.conf import settings
from festivals.models import Festival

class Wishlist(models.Model):  
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text="이 위시리스트를 등록한 회원입니다. (회원 탈퇴 시 삭제)"
    )
    festival = models.ForeignKey(
        Festival,
        on_delete=models.CASCADE,
        help_text="관심을 등록한 축제를 선택하세요. (축제 삭제 시 함께 삭제)"
    )
    notify = models.BooleanField(
        default=False,
        help_text="축제 일정 알림 여부 (ON: 알림, OFF: 알림 없음)"
    )
    added_date = models.DateTimeField(
        auto_now_add=True,
        help_text="위시리스트에 등록된 날짜(자동 입력)"
    )

    class Meta:
        unique_together = [('user', 'festival')]  # 한 회원이 같은 축제 중복 등록 불가

    def __str__(self):
        return f"{self.user.nickname} -> {self.festival.name}"  # username 대신 최신 설계에 맞게
