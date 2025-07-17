from django.contrib import admin
from .models import ShortForm, ShortFormImage

class ShortFormImageInline(admin.TabularInline):
    model = ShortFormImage # 제한 설정
    extra = 0  # 기본 추가 폼 수
    min_num = 1  # 최소 1장
    max_num = 6  # 최대 6장
    # 폼 개수 제한은 admin에선 이 옵션으로 어느 정도 가능

@admin.register(ShortForm)
class ShortFormAdmin(admin.ModelAdmin):
    inlines = [ShortFormImageInline]
    list_display = ['id', 'title', 'festival', 'user', 'created_at']
    # 필요에 따라 search_fields, list_filter 등 추가 가능

admin.site.register(ShortFormImage)