from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # 목록에서 보여줄 컬럼들
    list_display = ('id', 'username', 'email', 'login_type', 'social_id')
    # 검색 가능 필드
    search_fields = ('username', 'email', 'social_id')
    # 필터로 사용할 필드
    list_filter = ('login_type',)
    # 상세페이지에서 읽기전용 필드 (예시)
    readonly_fields = ('date_joined', 'last_login')

    # (추가로, interest_tags 등 M2M 필드는 기본 위젯 그대로 노출됨)

    # 객체 표시(상단에 제목)
    def __str__(self, obj):
        return obj.username

# 기존 방식처럼 admin.site.register(User)만 써도 되지만,
# 위처럼 하면 관리자 기능을 더 많이 커스터마이즈 가능!
