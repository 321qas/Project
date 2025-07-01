from django.db import models
from django.conf import settings
from festivals.models import Festival
from django.core.exceptions import ValidationError

class ShortForm(models.Model):
    festival = models.ForeignKey(
        Festival,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text="이 쇼츠가 관련된 축제를 선택하세요. (삭제시에도 쇼츠는 남고 [템플릿/뷰 등에서 null => '없어진 축제입니다' 전환 로직 작성 필요])"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text="쇼츠를 작성한 회원을 선택하세요. (탈퇴시에도 쇼츠는 남고 [템플릿/뷰 등에서 null => '탈퇴한 사용자' 전환 로직 작성 필요])"
    )
    title = models.CharField(
        max_length=50,
        help_text="쇼츠의 제목을 입력하세요. (필수)"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="쇼츠 등록일 (자동 생성)"
    )

    def __str__(self):
        # 축제가 삭제되었으면 안내 텍스트로 표시
        fest = self.festival.name if self.festival else '없어진 축제입니다'
        return f"{fest} - {self.title}"

    def image_count(self):
        "쇼츠에 첨부된 이미지 개수"
        return self.images.count()

class ShortFormImage(models.Model):
    shortform = models.ForeignKey(
        ShortForm,
        on_delete=models.CASCADE,
        related_name='images',
        help_text="이미지가 첨부될 쇼츠를 선택하세요."
    )
    image = models.ImageField(
        upload_to='shortforms/images/',
        help_text="업로드할 이미지 파일을 선택하세요. (최소 1장, 최대 6장)"
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        help_text="이미지 업로드 일시 (자동 생성)"
    )

    def clean(self):
        # 이미지가 1~6장 사이인지 유효성 검사
        if not self.shortform_id:
            return
        current_count = ShortFormImage.objects.filter(shortform=self.shortform).count()
        if not self.pk:
            current_count += 1
        if current_count < 1:
            raise ValidationError("최소 1장의 이미지를 등록해야 합니다.")
        if current_count > 6:
            raise ValidationError("최대 6장까지만 등록할 수 있습니다.")

    def __str__(self):
        return f"Image {self.id} for ShortForm {self.shortform.id}"
