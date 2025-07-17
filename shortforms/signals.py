# 이미지 인스턴스가 DB에서 삭제될 때, 실제 파일도 같이 삭제한다.
# apps.py에서 ready 메서드에 import shortforms.signals를 추가하여 signals를 등록해야 합니다.

from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import ShortFormImage

@receiver(post_delete, sender=ShortFormImage)
def delete_shortform_image_file(sender, instance, **kwargs):
    """
    ShortFormImage 객체가 삭제될 때 실제 이미지 파일도 같이 삭제
    - 예) 관리자가 이미지 삭제, 쇼츠(ShortForm) 삭제로 인한 cascade 삭제
    """
    if instance.image:
        instance.image.delete(save=False)
