from django.contrib import admin
from django.utils.html import format_html
from .models import Festival, FestivalImage, RegionInterest

class FestivalImageInline(admin.TabularInline):
    model = FestivalImage
    extra = 0
    min_num = 2
    max_num = 8
    readonly_fields = ('preview',)

    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height:100px; max-width:150px;" />', obj.image.url)
        return "-"
    preview.short_description = "이미지 미리보기"

class FestivalAdmin(admin.ModelAdmin):
    inlines = [FestivalImageInline]
    list_display = (
        'id', 'name', 'start_date', 'end_date', 'region', 'organizer',
        'visitor_count', 'display_tags', 'created_at', 'updated_at'
    )
    search_fields = (
        'name', 'organizer',
    )
    list_filter = (
        'region',
    )
    filter_horizontal = ('tags',)
    readonly_fields = ('created_at', 'updated_at')

    def display_tags(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])
    display_tags.short_description = '태그'

class RegionInterestAdmin(admin.ModelAdmin):
    list_display = ('region', 'count')
    list_filter = ('region',)
    search_fields = ('region',)

admin.site.register(Festival, FestivalAdmin)
admin.site.register(RegionInterest, RegionInterestAdmin)
