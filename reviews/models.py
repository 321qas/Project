from django.db import models
from django.conf import settings
from festivals.models import Festival
from django.core.exceptions import ValidationError

class Review(models.Model):  
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
    festival = models.ForeignKey(
        Festival,
        on_delete=models.CASCADE,
        help_text="후기를 작성할 축제를 선택하세요. (축제 삭제 시 후기 같이 삭제)"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text="후기를 작성한 회원입니다. (회원 탈퇴 시 삭제)"
    )
    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        default=5,
        help_text="축제 평점(1~5점 중 선택, 기본값 5점)"
    )
    content = models.TextField(
        help_text="후기 본문을 입력하세요."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="후기 작성일 (자동 입력)"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="후기 수정일 (자동 입력)"
    )

    def clean(self):
        # 이미지 개수 0~5장 제한
        if not self.pk:
            image_count = 0
        else:
            image_count = self.images.count()
        if image_count > 5:
            raise ValidationError("최대 5장까지만 이미지를 등록할 수 있습니다.")

    def __str__(self):
        return f"Review of {self.festival.name} by {self.user.nickname}"

class ReviewImage(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='images',
        help_text="이미지를 첨부할 후기를 선택하세요."
    )
    image_filename = models.CharField(
        max_length=255,
        help_text="이미지 파일의 이름 또는 경로를 입력하세요."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="이미지 업로드 일시 (자동 입력)"
    )

    def __str__(self):
        return f"Image for Review {self.review.id}"

class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        help_text="댓글을 작성할 후기를 선택하세요."
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text="댓글을 작성한 회원입니다. (회원 탈퇴 시 댓글도 삭제)"
    )
    content = models.TextField(
        help_text="댓글 내용을 입력하세요."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="댓글 작성일 (자동 입력)"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="댓글 수정일 (자동 입력)"
    )

    def __str__(self):
        return f"{self.user.nickname}'s comment on Review {self.review.id}"
