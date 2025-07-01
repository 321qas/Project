# 사진 인스턴스가 DB에서 삭제될 때, 실제 파일도 같이 삭제한다.
# apps.py에서 ready 메서드에 import festivals.signals를 추가하여 signals를 등록해야 합니다.

from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import ReviewImage

@receiver(post_delete, sender=ReviewImage)
def delete_review_image_file(sender, instance, **kwargs):
    """
    리뷰 이미지 객체가 삭제될 때, 실제 이미지 파일도 같이 삭제
    - 예: 관리자가 리뷰이미지 삭제 or 리뷰가 삭제되어 cascade로 이미지 삭제
    """
    if instance.image:
        instance.image.delete(save=False)  # 파일 시스템에서 이미지 삭제
