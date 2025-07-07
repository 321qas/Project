# 페스티벌 데이터 CSV 파일을 Festival 모델에 일괄 삽입하는 Django 커맨드입니다.
# 사용법: 터미널에 => python manage.py import_festivals --file=내csv파일.csv

import pandas as pd
import re
import os
from django.core.management.base import BaseCommand
from festivals.models import Festival

class Command(BaseCommand):
    help = 'CSV 파일 데이터를 Festival 테이블에 일괄 삽입합니다.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='CSV 파일 경로를 반드시 입력하세요 (예: --file=myfile.csv)',
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
        df = df.iloc[:196] # 196개 레코드만 사용
        
        # 4. 날짜/숫자 컬럼 포맷 맞추기
        for c in ['start_date', 'end_date']:
            df[c] = df[c].astype(str).str.replace('.', '-', regex=False)
            df[c] = pd.to_datetime(df[c], errors='coerce')
        for c in ['latitude', 'longitude']:
            df[c] = pd.to_numeric(df[c], errors='coerce')
        for c in ['visitor_count']:
            df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0).astype(int)
        

        df = df[df['start_date'].notnull()]

        # 5. Festival 객체로 변환
        objs = []
        for _, row in df.iterrows():
            # 전화번호에서 숫자만 남기기 (하이픈, 공백, 기타 문자 모두 제거)
            phone_raw = str(row['contact_phone']) if pd.notnull(row['contact_phone']) else ""
            phone_clean = re.sub(r'[^0-9]', '', phone_raw)

            obj = Festival(
                name=row['name'],
                description=row['description'],
                start_date=row['start_date'].date() if not pd.isnull(row['start_date']) else None,
                end_date=row['end_date'].date() if not pd.isnull(row['end_date']) else None,
                region=row['region'],
                detail_region=row['detail_region'],
                latitude=row['latitude'] if not pd.isnull(row['latitude']) else None,
                longitude=row['longitude'] if not pd.isnull(row['longitude']) else None,
                fee=row['fee'],
                organizer=row['organizer'],
                contact_phone=phone_clean,  # 정제된 번호만 저장!
                website_url=row['website_url'],
                visitor_count=row['visitor_count']
            )
            objs.append(obj)

        # 6. DB에 일괄 저장 (bulk_create는 대량 데이터 처리에 매우 빠름)
        Festival.objects.bulk_create(objs)

        # 7. 결과 출력
        self.stdout.write(self.style.SUCCESS(f'{len(objs)}개 레코드 삽입 완료!'))
