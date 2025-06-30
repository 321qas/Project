from django.db import models
from django.conf import settings

class Inquiry(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)  # 문의 작성 회원 (탈퇴 등으로 없을 수 있음)
    title = models.CharField(max_length=200)  # 문의 제목
    content = models.TextField()  # 문의 내용 (질문 본문)
    created_at = models.DateTimeField(auto_now_add=True)  # 문의 작성 시간
    response = models.TextField(blank=True)  # 관리자 답변 내용 (초기에는 비워둠)
    answered_at = models.DateTimeField(null=True, blank=True)  # 답변 등록 시간 (답변 시각 기록)
    is_answered = models.BooleanField(default=False)  # 답변 완료 여부

    def __str__(self):
        return f"Inquiry by {self.user.username if self.user else 'Anonymous'}: {self.title}"
