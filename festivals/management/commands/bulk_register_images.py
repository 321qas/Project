
# DB에 이미지 경로 자동등록을 위한 Django 커맨드 스크립트
# 사용법: 터미널에 => python manage.py bulk_register_images


import os
from django.core.management.base import BaseCommand
from django.conf import settings
from festivals.models import Festival, FestivalImage

class Command(BaseCommand):
    help = 'media/festivals/images/ 각 폴더 내 이미지를 FestivalImage로 등록 (폴더명=pk.축제명)'

    def handle(self, *args, **options):
        # 1. 상위 이미지 폴더
        root_dir = os.path.join(settings.MEDIA_ROOT, 'festivals', 'images')
        if not os.path.exists(root_dir):
            self.stdout.write(self.style.ERROR(f"폴더가 존재하지 않습니다: {root_dir}"))
            return

        total_registered = 0
        total_skipped = 0

        # 2. 폴더 탐색
        for folder in os.listdir(root_dir):
            folder_path = os.path.join(root_dir, folder)
            if not os.path.isdir(folder_path):
                continue

            # 폴더명: '1.춘천 막국수 닭갈비축제' 형식
            try:
                pk = int(folder.split('.')[0])
            except (IndexError, ValueError):
                self.stdout.write(self.style.WARNING(f"[SKIP] 잘못된 폴더명: {folder}"))
                total_skipped += 1
                continue

            # DB에서 해당 pk의 축제 찾기
            try:
                festival = Festival.objects.get(pk=pk)
            except Festival.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"[SKIP] Festival id={pk} 없음 (폴더: {folder})"))
                total_skipped += 1
                continue

            # 3. 폴더 안의 이미지 파일 등록
            files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
            if not files:
                self.stdout.write(self.style.WARNING(f"[SKIP] 이미지 없음: {folder}"))
                total_skipped += 1
                continue

            for fname in files:
                image_path = os.path.join('festivals', 'images', folder, fname)

                # 중복 체크
                if FestivalImage.objects.filter(festival=festival, image=image_path).exists():
                    self.stdout.write(self.style.NOTICE(f"[SKIP] 이미 등록: {image_path}"))
                    total_skipped += 1
                    continue

                FestivalImage.objects.create(
                    festival=festival,
                    image=image_path
                )
                self.stdout.write(self.style.SUCCESS(f"[OK] {festival.name} ← {fname}"))
                total_registered += 1

        self.stdout.write(self.style.SUCCESS(f"\n=== 작업 종료 ===\n성공: {total_registered}건, 스킵: {total_skipped}건"))
