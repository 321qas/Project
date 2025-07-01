from django.contrib import admin
from .models import Festival, FestivalImage
from django import forms

class FestivalImageInline(admin.TabularInline):
    model = FestivalImage
    extra = 0
    min_num = 2
    max_num = 8

class FestivalAdmin(admin.ModelAdmin): 
    inlines = [FestivalImageInline]
    list_display = ('name', 'start_date', 'end_date', 'region', 'organizer') # 목록에서 보여줄 컬럼들
    search_fields = ('name', 'organizer', 'description')  # 검색 필드 추가!
    list_filter = ('region',)  # 지역 필터


admin.site.register(Festival, FestivalAdmin)
admin.site.register(FestivalImage)
