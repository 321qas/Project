from django.contrib import admin
from .models import Festival, FestivalImage
from django import forms

class FestivalImageInline(admin.TabularInline):
    model = FestivalImage
    extra = 0
    min_num = 2
    max_num = 8

# 태그를 admin 목록, 필터, 검색, 폼에 모두 추가
class FestivalAdmin(admin.ModelAdmin):
    inlines = [FestivalImageInline]
    list_display = (
        'name', 'start_date', 'end_date', 'region', 'organizer', 'display_tags'
    )
    search_fields = ('name', 'organizer', 'description', 'tags__name')  # 태그 이름으로도 검색
    list_filter = ('region', 'tags')  # 태그별 필터 추가
    filter_horizontal = ('tags',)  # 태그를 좌우 선택 위젯으로 편하게

    def display_tags(self, obj):
        """어드민 목록에서 태그를 콤마로 연결해 보여줌"""
        return ", ".join([tag.name for tag in obj.tags.all()])
    display_tags.short_description = '태그'

admin.site.register(Festival, FestivalAdmin)
admin.site.register(FestivalImage)
