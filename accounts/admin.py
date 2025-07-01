from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # 목록에서 보여줄 컬럼들
    list_display = (
        'id',               # PK
        'user_id',          # 회원 아이디
        'display_nickname', # 닉네임
        'real_name',        # 실명
        'email',            # 이메일
        'login_type',       # 가입 방식
        'social_id',        # 소셜 고유ID
        'is_active',        # 활성여부
        'is_staff',         # 관리자여부
        'date_joined',      # 가입일
    )

    
    def display_nickname(self, obj):
        # 닉네임 없으면 '탈퇴한 회원'로 표시
        return obj.nickname if obj.nickname else '탈퇴한 회원'
    display_nickname.short_description = '닉네임'

    # 검색 필드
    search_fields = ('user_id', 'nickname', 'real_name', 'email', 'social_id')
    # 필터 필드
    list_filter = ('login_type', 'is_active', 'is_staff')
    # 읽기전용 필드(상세에서)
    readonly_fields = ('date_joined',)

    # ManyToManyField(interest_tags)는 기본 위젯 제공
    fieldsets = (
        (None, {
            'fields': (
                'user_id', 'email', 'nickname', 'real_name', 'phone_number',
                'login_type', 'social_id', 'interest_tags',
                'is_active', 'is_staff', 'is_superuser', 'date_joined'
            ),
            'description': '회원 기본정보와 권한을 설정합니다.'
        }),
    )

    def __str__(self, obj):
        return obj.user_id
