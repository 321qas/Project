from django.contrib import admin
from .models import Festival, FestivalImage

class FestivalImageInline(admin.TabularInline):
    model = FestivalImage # 제한 설정
    extra = 0 # 기본 추가 폼 수
    min_num = 2  # 최소 2장
    max_num = 8  # 최대 8장

class FestivalAdmin(admin.ModelAdmin):
    inlines = [FestivalImageInline] # 이미지 인라인 폼 페이지 변환 없이 등록
    list_display = ('name', 'start_date', 'end_date')

admin.site.register(Festival, FestivalAdmin)
admin.site.register(FestivalImage)
