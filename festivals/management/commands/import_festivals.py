# festivals/management/commands/import_festivals.py
# 사용법 : python manage.py import_festivals --file=F_Data.csv

import pandas as pd
from django.core.management.base import BaseCommand
from festivals.models import Festival
from tags.models import Tag    # <-- [1] Tag import
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
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"파일을 찾을 수 없습니다: {file_path}"))
            return

        df = pd.read_csv(file_path, encoding='utf-8-sig')
        df = df.dropna(how='all')
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
            'Tag': 'Tag',         # [2] Tag 컬럼 추가
        }
        df = df.rename(columns=col_map)

        region_display_to_key = {
            '서울': 'SEOUL', '부산': 'BUSAN', '제주': 'JEJU', '인천': 'INCHEON', '광주': 'GWANGJU',
            '대구': 'Daegu', '대전': 'Daejeon', '울산': 'Ulsan', '세종': 'Sejong', '경기': 'Gyeonggi',
            '충북': 'Chungbuk', '충남': 'Chungnam', '전남': 'jeonnam', '경북': 'Gyeongbuk', '경남': 'Gyeongnam',
            '강원': 'Gangwon', '전북': 'jeonbuk'
        }
        if 'region' in df.columns:
            df['region'] = df['region'].map(region_display_to_key).fillna('SEOUL')

        for c in ['start_date', 'end_date']:
            if c in df.columns:
                df[c] = df[c].astype(str).str.replace(r'[.]', '-', regex=True)
                df[c] = pd.to_datetime(df[c], errors='coerce').dt.strftime('%Y-%m-%d')

        for c in ['latitude', 'longitude']:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors='coerce')
        if 'visitor_count' in df.columns:
            df['visitor_count'] = pd.to_numeric(df['visitor_count'], errors='coerce').fillna(0).astype(int)

        if 'contact_phone' in df.columns:
            df['contact_phone'] = df['contact_phone'].astype(str).str.replace('-', '', regex=False)

        objs, skipped, row_idx_map = [], 0, {}
        for i, row in df.iterrows():
            if Festival.objects.filter(name=row['name'], start_date=row['start_date']).exists():
                skipped += 1
                continue
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
            row_idx_map[len(objs)-1] = i  # [3] objs 인덱스 <-> df 인덱스 매핑

        Festival.objects.bulk_create(objs)

        # [4] 방금 bulk_create된 객체들 가져와서 Tag 연결
        if objs and 'Tag' in df.columns:
            inserted_fests = list(Festival.objects.filter(
                name__in=[o.name for o in objs],
                start_date__in=[o.start_date for o in objs]
            ))

            for idx, fest in enumerate(inserted_fests):
                i = row_idx_map.get(idx)
                if i is not None:
                    tags_str = df.loc[i, 'Tag']
                    if pd.notnull(tags_str):
                        tag_names = [t.strip() for t in str(tags_str).split(',') if t.strip()]
                        for tag_name in tag_names:
                            tag_obj, _ = Tag.objects.get_or_create(name=tag_name)
                            fest.tags.add(tag_obj)

        self.stdout.write(self.style.SUCCESS(f'{len(objs)}개 레코드 삽입 완료! (중복 {skipped}건 제외)'))

