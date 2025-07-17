
# FestivalImage 인스턴스가 DB에서 삭제될 때, 실제 파일도 같이 삭제한다.
# apps.py에서 ready 메서드에 import festivals.signals를 추가하여 signals를 등록해야 합니다.

from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import FestivalImage

@receiver(post_delete, sender=FestivalImage)
def delete_image_file_on_festivalimage_delete(sender, instance, **kwargs):
    if instance.image:
        instance.image.delete(save=False)
