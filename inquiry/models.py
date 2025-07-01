from django.db import models
from django.conf import settings

class Inquiry(models.Model):                                 # 문의글
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        help_text="문의글을 작성한 회원을 선택하세요. (회원 탈퇴시 문의글도 삭제됨)"
    ) 
    title = models.CharField(
        max_length=100,
        help_text="문의글의 제목을 입력하세요."
    )
    content = models.TextField(
        help_text="문의 내용을 자세히 입력하세요."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="문의글 작성일(자동 입력)"
    )
    STATUS_CHOICES = (
        ('waiting', '접수'),      # 접수 (대기중)
        ('answered', '답변완료'), # 답변 등록됨
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='waiting',   # 기본값: 접수
        help_text="문의 처리 상태 (접수, 답변완료중 선택)"
    )

    def __str__(self):
        # user.nickname을 쓰는 게 최신 설계와 맞음. username이 없을 수도 있음
        return f"{self.title} ({getattr(self.user, 'nickname', self.user.pk)})"

class InquiryReply(models.Model):                            # 답변글
    inquiry = models.ForeignKey(
        Inquiry,
        on_delete=models.CASCADE,
        related_name='replies',
        help_text="어떤 문의글에 대한 답변인지 선택하세요."
    )
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, null=True, blank=True,
        help_text="답변을 작성한 관리자 계정(선택사항, 삭제시에도 답변 보존)."
    )
    content = models.TextField(
        help_text="답변 내용을 입력하세요."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="답변 작성일(자동 입력)"
    )

    def __str__(self):
        return f"Reply to Inquiry {self.inquiry.id}"
