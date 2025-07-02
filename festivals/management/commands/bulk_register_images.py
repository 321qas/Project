
# DB에 이미지 경로 자동등록을 위한 Django 커맨드 스크립트
# 사용법: 터미널에 => python manage.py bulk_register_images


import os
from django.core.management.base import BaseCommand
from django.conf import settings
from festivals.models import Festival, FestivalImage  # 실제 앱/모델명에 맞게 수정

class Command(BaseCommand):
    help = 'media/festivals/images/ 폴더 내 이미지 파일을 일괄적으로 FestivalImage로 등록'

    def handle(self, *args, **options):
        # 1. 실제 이미지가 저장된 폴더 (MEDIA_ROOT 기반)
        image_dir = os.path.join(settings.MEDIA_ROOT, 'festivals', 'images')
        if not os.path.exists(image_dir):
            self.stdout.write(self.style.ERROR(f"폴더가 존재하지 않습니다: {image_dir}"))
            return

        # 2. 이미지 파일 리스트업
        files = [f for f in os.listdir(image_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
        if not files:
            self.stdout.write(self.style.WARNING("이미지 파일이 없습니다."))
            return

        registered = 0
        skipped = 0
        for fname in files:
            # 언더바('_')가 없는 파일은 건너뜀
            if '_' in fname:
                festival_name = '_'.join(fname.split('_')[:-1])
            else:
                self.stdout.write(self.style.WARNING(f"[SKIP] 잘못된 파일명 형식: {fname}"))
                skipped += 1
                continue

            # 축제명으로 DB에서 찾기
            try:
                festival = Festival.objects.get(name=festival_name)
            except Festival.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"[SKIP] Festival not found: {festival_name} (file: {fname})"))
                skipped += 1
                continue

            image_path = os.path.join('festivals', 'images', fname)

            # 중복 체크
            if FestivalImage.objects.filter(festival=festival, image=image_path).exists():
                self.stdout.write(self.style.NOTICE(f"[SKIP] 이미 등록된 이미지: {image_path}"))
                skipped += 1
                continue

            FestivalImage.objects.create(
                festival=festival,
                image=image_path
            )
            self.stdout.write(self.style.SUCCESS(f"[OK] 등록 완료: {festival_name} → {fname}"))
            registered += 1

        self.stdout.write(self.style.SUCCESS(f"\n=== 작업 종료 ===\n성공: {registered}건, 스킵: {skipped}건"))
