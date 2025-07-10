from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # 목록에 보여줄 필드
    list_display = (
        'id',               # DB PK (int형이라면 자동)
        'user_id',          # 회원 아이디
        'display_nickname', # 닉네임 (별도 표시 함수)
        'real_name',        # 실명
        'email',            # 이메일
        'login_type',       # 가입 방식
        'social_id',        # 소셜 고유ID
        'gender',           # 성별
        'dob',              # 생년월일
        'is_active',        # 활성여부
        'is_staff',         # 관리자여부
        'date_joined',      # 가입일
    )

    # 닉네임이 없으면 '탈퇴한 회원'으로 표시
    def display_nickname(self, obj):
        return obj.nickname if obj.nickname else '탈퇴한 회원'
    display_nickname.short_description = '닉네임'

    # 검색 필드
    search_fields = (
        'user_id', 'nickname', 'real_name', 'email', 'social_id', 'gender', 'dob'
    )

    # 리스트 필터
    list_filter = (
        'login_type', 'gender', 'is_active', 'is_staff'
    )

    # 읽기전용 필드 (상세/수정 화면)
    readonly_fields = ('date_joined',)

    # 필드 그룹화
    fieldsets = (
        (None, {
            'fields': (
                'user_id', 'email', 'nickname', 'real_name', 'phone_number',
                'gender', 'dob',
                'login_type', 'social_id', 'interest_tags',
                'is_active', 'is_staff', 'is_superuser', 'date_joined'
            ),
            'description': '회원 기본정보와 권한을 설정합니다.'
        }),
    )
