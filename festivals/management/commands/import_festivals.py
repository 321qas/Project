# festivals/management/commands/import_festivals.py
# 사용법: python manage.py import_festivals --file=F_Data.csv

import pandas as pd
from django.core.management.base import BaseCommand
from festivals.models import Festival
import os

class Command(BaseCommand):
    help = 'CSV 파일 데이터를 Festival 테이블에 일괄 삽입합니다.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='CSV 파일 경로를 반드시 입력하세요 (예: --file=F_Data.csv)',
            required=True,
        )

    def handle(self, *args, **options):
        file_path = options['file']

        # 1. 파일 존재 여부 체크
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"파일을 찾을 수 없습니다: {file_path}"))
            return

        # 2. CSV 파일 읽기
        df = pd.read_csv(file_path, encoding='utf-8-sig')

        # 3. 모든 컬럼이 NaN인 행은 삭제 (빈 줄 등 예외 방지)
        df = df.dropna(how='all')

        # 4. 컬럼명 매핑 (한글 → 모델 필드명)
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

        # 5. 한글 지역명을 영문키로 변환
        region_display_to_key = {
            '서울': 'SEOUL', '부산': 'BUSAN', '제주': 'JEJU', '인천': 'INCHEON', '광주': 'GWANGJU',
            '대구': 'Daegu', '대전': 'Daejeon', '울산': 'Ulsan', '세종': 'Sejong', '경기': 'Gyeonggi',
            '충북': 'Chungbuk', '충남': 'Chungnam', '전남': 'jeonnam', '경북': 'Gyeongbuk', '경남': 'Gyeongnam',
            '강원': 'Gangwon', '전북': 'jeonbuk'
        }
        if 'region' in df.columns:
            df['region'] = df['region'].map(region_display_to_key).fillna('SEOUL')

        # 6. 날짜/숫자 포맷 변환
        for c in ['start_date', 'end_date']:
            if c in df.columns:
                # "2025.03.23" -> "2025-03-23"
                df[c] = df[c].astype(str).str.replace(r'[.]', '-', regex=True)
                df[c] = pd.to_datetime(df[c], errors='coerce').dt.strftime('%Y-%m-%d')

        for c in ['latitude', 'longitude']:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors='coerce')
        if 'visitor_count' in df.columns:
            df['visitor_count'] = pd.to_numeric(df['visitor_count'], errors='coerce').fillna(0).astype(int)

        # 7. 연락처 하이픈 제거
        if 'contact_phone' in df.columns:
            df['contact_phone'] = df['contact_phone'].astype(str).str.replace('-', '', regex=False)

        # 8. Festival 객체로 변환 (필드별로 빈값 허용 여부는 모델 기준)
        objs = []
        for _, row in df.iterrows():
            obj = Festival(
                name=row['name'],
                description=row['description'],
                start_date=row['start_date'],
                end_date=row['end_date'],
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

        # 9. DB에 일괄 저장
        Festival.objects.bulk_create(objs)
        self.stdout.write(self.style.SUCCESS(f'{len(objs)}개 레코드 삽입 완료!'))
