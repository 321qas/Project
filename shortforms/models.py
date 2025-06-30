from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

class ShortForm(models.Model):
    festival = models.ForeignKey(
        'festivals.Festival',
        on_delete=models.SET_NULL,         # 축제가 삭제되어도 숏폼은 남고 festival 필드만 null로 변경
        null=True, blank=True              # festival 필드는 null 허용 (필수)
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,         # 회원이 탈퇴해도 숏폼은 남고 user 필드만 null로 변경
        null=True, blank=True              # user 필드는 null 허용 (필수)
    )
    title = models.CharField(max_length=100)                  # 숏폼 제목 (100자 제한)
    caption = models.CharField(max_length=255, blank=True)    # 설명/캡션 (선택사항)
    created_at = models.DateTimeField(auto_now_add=True)      # 생성일시(업로드 시 자동 저장)

    def clean(self): # 모델 저장 전 유효성 검사 및 오류 메세지 출력
        # 저장 전 이미지 장수 확인 (DB에 저장된 + 폼에서 추가된)
        count = self.images.count()
        if self.pk:  # 이미 저장된 객체일 때만 count
            # Inlines로 등록된 새 이미지까지 합산하려면 폼에서 추가 검증 필요
            if count < 1:
                raise ValidationError("이미지는 최소 1장 이상 등록해야 합니다.")
            if count > 6:
                raise ValidationError("이미지는 최대 6장까지만 등록할 수 있습니다.")

    def __str__(self):
        # 축제 또는 유저가 삭제되어도 오류나지 않게 표시
        fest = self.festival.name if self.festival else '[삭제된 축제]'
        return f"{fest} - {self.title}"

    def image_count(self):
        # 연결된 이미지 개수 반환 (폼에서 개수 제한시 활용)
        return self.images.count()

class ShortFormImage(models.Model):
    shortform = models.ForeignKey(
        ShortForm,
        on_delete=models.CASCADE,           # 숏폼이 삭제되면 연결된 이미지는 같이 삭제
        related_name='images'               # shortform.images.all()로 접근 가능
    )
    image = models.ImageField(upload_to='shortforms/images/') # 실제 업로드 이미지 파일 경로
    uploaded_at = models.DateTimeField(auto_now_add=True)     # 이미지 업로드 시각

    def __str__(self):
        # 이미지의 간단한 정보 표시
        return f"Image {self.id} for ShortForm {self.shortform.id}"

