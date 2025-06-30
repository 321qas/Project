from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

class Review(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
    festival = models.ForeignKey('festivals.Festival', on_delete=models.CASCADE)   # 어느 축제 후기인지
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)   # 작성자
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, default=5)   # 평점 1~5
    content = models.TextField()                  # 후기 본문
    created_at = models.DateTimeField(auto_now_add=True)   # 생성일
    updated_at = models.DateTimeField(auto_now=True)       # 수정일

    def clean(self):
        image_count = self.images.count()
        if image_count > 5:
            raise ValidationError("이미지는 최대 5장까지만 등록할 수 있습니다.")

    def __str__(self):
        return f"Review of {self.festival.name} by {self.user.username}"
    def __str__(self):
        return f"Review of {self.festival.name} by {self.user.username}"

class ReviewImage(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='images')  # 어떤 후기의 이미지인지
    image_filename = models.CharField(max_length=255)   # 이미지 파일명/경로
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for Review {self.review.id}"

class Comment(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='comments')  # 어느 후기의 댓글인지
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)           # 댓글 작성자
    content = models.TextField()                  # 댓글 내용
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s comment on Review {self.review.id}"
