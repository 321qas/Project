# 페스티벌 데이터 CSV 파일을 Festival 모델에 일괄 삽입하는 Django 커맨드입니다.
# 사용법: 터미널에 => python manage.py import_festivals --file=내csv파일.csv


import pandas as pd
from django.core.management.base import BaseCommand
from festivals.models import Festival
import os

class Command(BaseCommand):
    help = 'CSV 파일(festival_model_with_visitors_final.csv) 데이터를 Festival 테이블에 일괄 삽입합니다.'

    def add_arguments(self, parser):
        # --file 옵션으로 csv 파일 경로 지정 가능 (root 가 아니면 Ex. python manage.py import_festivals --file=data/내csv파일.csv)
        parser.add_argument(
            '--file',
            type=str,
            help='CSV 파일 경로를 반드시 입력하세요 (예: 위치가 root 일경우 --file=myfile.csv)',
            required=True,
        )

    def handle(self, *args, **options):
        file_path = options['file']
        # 1. 파일 존재 여부 체크
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"파일을 찾을 수 없습니다: {file_path}"))
            return

        # 2. CSV 파일 읽어오기 (한글 컬럼 포함)
        df = pd.read_csv(file_path, encoding='utf-8-sig')

        # 3. 컬럼명(한글포함) → 모델 필드명으로 매핑
        col_map = {
            'name(이름)': 'name',
            'description(설명)': 'description',
            'start_date(시작일)': 'start_date',
            'end_date(종료일)': 'end_date',
            'region(지역)': 'region',
            'detail_region(상세지역)': 'detail_region',
            'latitude(위도)': 'latitude',
            'longitude(경도)': 'longitude',
            'fee(참가요금)': 'fee',
            'organizer(주최기관)': 'organizer',
            'contact_phone(연락처)': 'contact_phone',
            'website_url(공식홈페이지)': 'website_url',
            'visitor_count(방문객수)': 'visitor_count',
        }
        df = df.rename(columns=col_map)

        # 4. 날짜/숫자 컬럼 포맷 맞추기 (모델에 들어갈 수 있는 형태로 변환)
        # 날짜: YYYY-MM-DD, 숫자: NaN→None, 빈칸→0 등 처리
        for c in ['start_date', 'end_date']:
            df[c] = pd.to_datetime(df[c], errors='coerce').dt.strftime('%Y-%m-%d')
        for c in ['latitude', 'longitude']:
            df[c] = pd.to_numeric(df[c], errors='coerce')
        for c in ['fee', 'visitor_count']:
            df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0).astype(int)

        # 5. Festival 객체로 변환
        objs = []
        for _, row in df.iterrows():
            obj = Festival(
                name=row['name'],
                description=row['description'],
                start_date=row['start_date'] if row['start_date'] else None,
                end_date=row['end_date'] if row['end_date'] else None,
                region=row['region'],
                detail_region=row['detail_region'],
                latitude=row['latitude'] if not pd.isnull(row['latitude']) else None,
                longitude=row['longitude'] if not pd.isnull(row['longitude']) else None,
                fee=row['fee'],
                organizer=row['organizer'],
                contact_phone=row['contact_phone'],
                website_url=row['website_url'],
                visitor_count=row['visitor_count']
            )
            objs.append(obj)

        # 6. DB에 일괄 저장 (bulk_create는 대량 데이터 처리에 매우 빠름)
        Festival.objects.bulk_create(objs)

        # 7. 결과 출력
        self.stdout.write(self.style.SUCCESS(f'{len(objs)}개 레코드 삽입 완료!'))
