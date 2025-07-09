from django.db import models
from django.contrib.auth.models import (AbstractBaseUser, PermissionsMixin, BaseUserManager)
from tags.models import Tag
from django.utils import timezone
import uuid, datetime

# 소셜로그인 시 회원의 아이디 자동생성 함수
def generate_social_user_id(login_type):
    return f"{login_type}_{uuid.uuid4().hex[:4]}" # 예: kakao_1234, naver_abcd

# 커스텀 User 매니저
class UserManager(BaseUserManager):
    def create_user(self, user_id=None, email=None, password=None, login_type='local', **extra_fields):
        if not email:
            raise ValueError("이메일은 필수입니다.")
        if not user_id:
            if login_type != 'local':
                user_id = generate_social_user_id(login_type)
            else:
                raise ValueError("아이디는 필수입니다.")
        email = self.normalize_email(email)
        user = self.model(
            user_id=user_id,
            email=email,
            login_type=login_type,
            **extra_fields
        )
        # 소셜 회원은 비밀번호 없음/None, 일반회원은 반드시 있음
        if login_type == 'local':
            if not password:
                raise ValueError("비밀번호는 필수입니다.")
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, user_id, email, password=None, **extra_fields): # 슈퍼유저 생성시 사용 (권한부여)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(user_id, email, password, login_type='local', **extra_fields)

# User 모델
class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.CharField(
        max_length=30, unique=True,
        help_text="서비스 내 회원 아이디. (소셜회원은 자동생성)")
    email = models.EmailField(
        unique=True,
        help_text="로그인/알림용 이메일 주소 (중복 불가)")
    nickname = models.CharField(
        max_length=30, unique=True, default="",
        help_text="닉네임(중복 불가, 필수)")
    real_name = models.CharField(
        max_length=30,
        help_text="사용자 본명(필수)")
    phone_number = models.CharField(
        max_length=15, blank=True,
        help_text="연락처(선택)")
    interest_tags = models.ManyToManyField(
        Tag, blank=True,related_name='user_set',
        help_text="관심 태그")
    is_active = models.BooleanField(default=True, help_text="계정 활성화 여부")
    is_staff = models.BooleanField(default=False, help_text="관리자 권한 여부")

    LOGIN_CHOICES = (
        ('local', '일반가입'),
        ('kakao', 'kakao'),
        ('naver', 'naver'),)
    login_type = models.CharField(
        max_length=10,
        choices=LOGIN_CHOICES,
        default='local',
        help_text='계정 생성 방식 (local, kakao, naver 등)')
    social_id = models.CharField(
        max_length=100, blank=True, null=True,
        help_text='소셜로그인 회원 고유ID')
    GENDER_CHOICES = (
        ('male', '남자'),
        ('female', '여자'),)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    dob = models.CharField(max_length=16, blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True, help_text="회원 가입일")

    objects = UserManager()

    USERNAME_FIELD = 'user_id'    # 로그인에 사용하는 필드 (아이디)
    REQUIRED_FIELDS = ['email', 'nickname', 'real_name']

    def __str__(self):
        return f"{self.user_id} / {self.nickname}"

    class Meta:
        verbose_name = "회원"
        verbose_name_plural = "회원"

# 이메일 인증 모델
class EmailVerification(models.Model):
    email = models.EmailField(unique=True)
    token = models.CharField(max_length=64, unique=True)
    user_id = models.CharField(max_length=32)
    password = models.CharField(max_length=128)
    real_name = models.CharField(max_length=32)
    nickname = models.CharField(max_length=32)
    gender = models.CharField(max_length=10, blank=True, null=True)
    dob = models.CharField(max_length=16, blank=True, null=True)
    tags = models.CharField(max_length=255, blank=True)  # 예: "여행,음악,사진"
    created_at = models.DateTimeField(auto_now_add=True)