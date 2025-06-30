from django.contrib import admin
from .models import Review, ReviewImage, Comment

class ReviewImageInline(admin.TabularInline):
    model = ReviewImage # 제한 설정
    extra = 0           # 기본 표시 이미지 폼 개수
    min_num = 0         # 0장도 허용
    max_num = 4         # 최대 4장 제한

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    inlines = [ReviewImageInline]
    list_display = ['id', 'festival', 'user', 'rating', 'created_at']

admin.site.register(Comment)
