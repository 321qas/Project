from django.db import models
from django.core.exceptions import ValidationError
from tags.models import Tag

class Festival(models.Model):
    name = models.CharField(
        max_length=100,
        help_text="축제 공식 명칭을 입력하세요. (예: 서울불꽃축제)")
    description = models.TextField(
        help_text="축제 상세 설명을 입력하세요.")
    start_date = models.DateField(
        help_text="축제 시작 날짜를 선택하세요. (예: 2025-05-10)")
    end_date = models.DateField(
        help_text="축제 종료 날짜를 선택하세요. (예: 2025-05-12)")
    REGION_CHOICES = [
        ('Seoul', 'Seoul'),('Busan', 'Busan'),('Jeju', 'Jeju'),
        ('Incheon', 'Incheon'),('Gwangju', 'Gwangju'),('Daegu', 'Daegu'),
        ('Daejeon', 'Daejeon'),('Ulsan', 'Ulsan'),('Sejong', 'Sejong'),
        ('Gyeonggi', 'Gyeonggi'),('Chungbuk', 'Chungbuk'),('Chungnam', 'Chungnam'),
        ('Jeonnam', 'Jeonnam'),('Gyeongbuk', 'Gyeongbuk'),('Gyeongnam', 'Gyeongnam'),
        ('Gangwon', 'Gangwon'),('Jeonbuk', 'Jeonbuk'),
    ]
    region = models.CharField(
        max_length=20, choices=REGION_CHOICES, default='SEOUL',
        help_text="주요 지역(시/도)을 선택하세요.")
    detail_region = models.CharField(
        max_length=100,
        help_text="축제가 개최되는 상세 주소를 입력하세요.")
    latitude = models.DecimalField(
        max_digits=10, decimal_places=7, blank=True, null=True,
        help_text="축제 위치의 위도를 입력하세요. (예: 37.5665357)")
    longitude = models.DecimalField(
        max_digits=10, decimal_places=7, blank=True, null=True,
        help_text="축제 위치의 경도를 입력하세요. (예: 126.9779692)")
    fee = models.CharField(
        max_length=70,
        default=0,
        help_text="참가 요금을 원 단위로 입력하세요. (무료이면 0 입력)")
    organizer = models.CharField(
        max_length=100, blank=True,
        help_text="축제 주최 기관 또는 부서를 입력하세요. (선택사항)")
    contact_phone = models.CharField(
        max_length=12, blank=True,
        help_text="문의 전화번호를 숫자만 입력하세요. (예: 0212345678, 선택사항)")
    website_url = models.URLField(
        max_length=300,
        null=True, blank=True,
        help_text="축제 공식 웹사이트 주소를 입력하세요. (선택사항)")
    visitor_count = models.PositiveIntegerField(
        default=0,
        help_text="축제 방문객 수(명)")
    tags = models.ManyToManyField(  # 축제 하나에 여러 태그, 태그 하나가 여러 축제에 할당될 수 있는 N:N 관계
        Tag,
        blank=True,
        related_name="festivals",
        help_text="축제와 관련된 태그를 여러 개 선택하세요.")
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="데이터가 등록된 일시(자동 입력).")
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="데이터가 마지막으로 수정된 일시(자동 입력).")
    

    def __str__(self):
        return f"{self.name} ({self.start_date} ~ {self.end_date})"

class RegionInterest(models.Model):
    region = models.CharField(
        max_length=20, choices=Festival.REGION_CHOICES, unique=True,
        help_text="지역(시/도)을 선택하세요. (중복 불가)")
    count = models.PositiveIntegerField(
        default=0,
        help_text="지역별 상세페이지 방문 누적 횟수.")

    def __str__(self):
        return f"{self.get_region_display()} (관심도: {self.count})"

class FestivalImage(models.Model):
    festival = models.ForeignKey(
        Festival, on_delete=models.CASCADE, related_name='images',
        help_text="이미지가 소속된 축제를 선택하세요.")
    image = models.ImageField(
        upload_to='festivals/images/',
        help_text="축제 대표 이미지를 업로드하세요. (최대 2MB, 2~8장)")
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        help_text="이미지가 업로드된 일시(자동 입력).")

    def clean(self):
        # 개수 제한 (2~8장)
        if not self.festival_id:
            return
        current_count = FestivalImage.objects.filter(festival=self.festival).count()
        if not self.pk:  # 새로 추가할 때
            current_count += 1
        if current_count < 2:
            raise ValidationError("각 축제는 최소 2장 이상의 이미지를 등록해야 합니다.")
        if current_count > 8:
            raise ValidationError("각 축제는 최대 8장까지만 이미지를 등록할 수 있습니다.")

        # 용량 제한 (2MB 이하)
        max_size = 2 * 1024 * 1024  # 2MB
        if self.image and self.image.size > max_size:
            raise ValidationError("이미지 파일은 2MB 이하만 업로드할 수 있습니다.")

    def __str__(self):
        return f"Image {self.id} for {self.festival.name}"
