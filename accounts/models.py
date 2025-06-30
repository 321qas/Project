from django.db import models                # Django의 ORM을 위한 models 모듈 임포트
from django.contrib.auth.models import AbstractUser  # 기본 User 확장을 위한 AbstractUser 임포트
from tags.models import Tag                  # 사용자의 관심 태그를 위한 Tag 모델 임포트

class User(AbstractUser):                    # Django 기본 유저 모델을 상속해서 사용자 정의 User 모델 정의
    email = models.EmailField(unique=True)    # 이메일 필드, unique=True로 설정해 같은 이메일로 두 번 가입 불가
    phone_number = models.CharField(max_length=15, blank=True)    # 전화번호 필드(최대 15자), 입력 안 해도 됨(blank=True)

    interest_tags = models.ManyToManyField(Tag, blank=True)       # 사용자가 여러 관심 태그를 선택할 수 있는 ManyToMany 관계(선택사항)

    # 소셜로그인 타입을 구분하기 위한 choice 필드 정의
    LOGIN_CHOICES = (
        ('local', '일반가입'),                # 자체 회원가입(local)
        ('kakao', '카카오'),                  # 카카오 로그인
        ('naver', '네이버'),                  # 네이버 로그인
    )
    login_type = models.CharField(
        max_length=10,                        # 최대 10자(로컬, 카카오, 네이버)
        choices=LOGIN_CHOICES,                # 위에서 정의한 선택지 중 하나만 입력 가능
        default='local',                      # 기본값은 'local'(일반 회원가입)
        help_text='계정 생성 방식을 구분 (local, kakao, naver 등)'  # 관리자 등에서 안내 문구
    )

    social_id = models.CharField(
        max_length=100,                       # 소셜에서 받은 유니크한 ID값(카카오, 네이버 등)
        blank=True, null=True,                # 소셜로그인 아닌 경우 비워둘 수 있음
        help_text='카카오/네이버 등 소셜 회원 고유 ID'
    )

    def __str__(self):                        # 객체를 문자열로 출력할 때 username을 보여줌(관리자, 쉘 등에서)
        return self.username
