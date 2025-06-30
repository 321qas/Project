from django.db import models
from django.core.exceptions import ValidationError

class Festival(models.Model):
    name = models.CharField(max_length=100, help_text="축제 공식 명칭 입력 (예: 서울불꽃축제)")
    description = models.TextField(help_text="축제 상세 설명 입력")
    start_date = models.DateField(help_text="축제 시작 날짜 (예: 2025-05-10)")
    end_date = models.DateField(help_text="축제 종료 날짜 (예: 2025-05-12)")
    REGION_CHOICES = [
        ('SEOUL', '서울'), ('BUSAN', '부산'), ('JEJU', '제주'), ('INCHEON', '인천'), ('GWANGJU', '광주'),
        ('Daegu', '대구'), ('Daejeon', '대전'), ('Ulsan', '울산'), ('Sejong', '세종'), ('Gyeonggi', '경기도'),
        ('Chungbuk', '충북'), ('Chungnam', '충남'), ('jeonbuk', '전북'), ('jeonnam', '전남'),
        ('Gyeongbuk', '경북'), ('Gyeongnam', '경남'), ('Gangwon', '강원도'),
    ]
    region = models.CharField(max_length=20, choices=REGION_CHOICES, default='SEOUL', help_text="주요 지역(시/도) 선택")
    detail_region = models.CharField(max_length=100, help_text="개최 장소 전체 주소 입력")
    fee = models.PositiveIntegerField(default=0, help_text="참가 요금(원) 입력, 무료면 0")
    organizer = models.CharField(max_length=100, blank=True, help_text="주최 기관/부서 입력")
    contact_phone = models.CharField(max_length=12, blank=True, help_text="연락처 숫자만 입력 (예: 0212345678)")
    website_url = models.URLField(null=True, blank=True, help_text="공식 웹사이트 주소 입력")
    latitude = models.FloatField(null=True, blank=True, help_text="축제 개최 장소의 위도")
    longitude = models.FloatField(null=True, blank=True, help_text="축제 개최 장소의 경도")
    created_at = models.DateTimeField(auto_now_add=True, help_text="등록 일시 (자동 생성)")
    updated_at = models.DateTimeField(auto_now=True, help_text="수정 일시 (자동 갱신)")

    def __str__(self):
        return f"{self.name} ({self.start_date} ~ {self.end_date})"

class RegionInterest(models.Model): # 지역별 관심도 카운트 모델 
    region = models.CharField(max_length=20, choices=Festival.REGION_CHOICES, unique=True, help_text="지역(시/도) 선택")
    count = models.PositiveIntegerField(default=0, help_text="지역별 상세페이지 방문수")

    def __str__(self):
        return f"{self.get_region_display()} (관심도: {self.count})"

class FestivalImage(models.Model): # 축제 이미지 모델
    festival = models.ForeignKey(Festival, on_delete=models.CASCADE, related_name='images', help_text="이미지 소속 축제 선택")
    image = models.ImageField(upload_to='festivals/images/', help_text="축제 이미지 업로드")
    uploaded_at = models.DateTimeField(auto_now_add=True, help_text="이미지 업로드 일시")

    def clean(self): # 모델 저장 전 유효성 검사 및 오류 메세지 출력
        # self.festival이 아직 저장 전(신규 축제 등록 중)이라면 검증을 패스
        if not self.festival_id:
            return
        
        # 새 이미지를 추가했을 때 전체 이미지 장수 체크
        # self.pk가 없으면 추가(insert), 있으면 수정(update)
        current_count = FestivalImage.objects.filter(festival=self.festival).count()
        # 추가일 때는 아직 DB에 저장 안 되어 있으니 +1
        if not self.pk:
            current_count += 1
        # 이미지 개수 2~8장 사이만 허용
        if current_count < 2:
            raise ValidationError("각 축제는 최소 2장 이상의 이미지를 등록해야 합니다.")
        if current_count > 8:
            raise ValidationError("각 축제는 최대 8장까지만 이미지를 등록할 수 있습니다.")

    def __str__(self):
        return f"Image {self.id} for {self.festival.name}"
