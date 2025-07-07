from django.contrib import admin
from .models import Festival, FestivalImage, RegionInterest

class FestivalImageInline(admin.TabularInline):
    """축제별 이미지를 인라인으로 관리"""
    model = FestivalImage
    extra = 0
    min_num = 2
    max_num = 8

class FestivalAdmin(admin.ModelAdmin):
    """축제 관리자 화면"""
    inlines = [FestivalImageInline]
    list_display = (
        'id',
        'name', 'start_date', 'end_date', 'region', 'organizer',
        'visitor_count', 'display_tags'
    )
    search_fields = (
        'name', 'organizer', 'tags__name',
    )
    list_filter = (
        'region', 'tags',
    )
    filter_horizontal = ('tags',)  # 태그 편집 편하게

    def display_tags(self, obj):
        """어드민 목록에서 태그를 콤마로 연결해 보여줌"""
        return ", ".join([tag.name for tag in obj.tags.all()])
    display_tags.short_description = '태그'

class RegionInterestAdmin(admin.ModelAdmin):
    list_display = ('region', 'count')
    list_filter = ('region',)
    search_fields = ('region',)

admin.site.register(Festival, FestivalAdmin)
admin.site.register(FestivalImage)
admin.site.register(RegionInterest, RegionInterestAdmin)
