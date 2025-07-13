from django.contrib import admin
from .models import Review, ReviewImage, Comment

class ReviewImageInline(admin.TabularInline):
    model = ReviewImage
    extra = 0
    min_num = 0
    max_num = 4

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    inlines = [ReviewImageInline]
    list_display = ['user', 'festival', 'rating', 'created_at']
    search_fields = ['user__username', 'festival__name', 'content']

admin.site.register(Comment)
