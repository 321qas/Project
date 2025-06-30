from django.contrib import admin
from .models import Tag

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'user_count')  # 표에 태그명, 관심유저 수 출력

    def user_count(self, obj):
        return obj.user_set.count()  # ManyToManyField에서 역참조 기본명은 user_set
    user_count.short_description = '관심 유저 수'
