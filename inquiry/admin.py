from django.contrib import admin
from .models import Inquiry, InquiryReply

# InquiryReply(답변)를 Inquiry(문의) 인라인으로 보여주기
class InquiryReplyInline(admin.StackedInline):
    model = InquiryReply
    extra = 0
    readonly_fields = ('created_at',)
    can_delete = False

@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user', 'status', 'created_at')  # 목록에서 보이는 필드
    list_filter = ('status', 'created_at')                          # 필터링
    search_fields = ('title', 'content', 'user__nickname')          # 검색
    readonly_fields = ('created_at',)
    inlines = [InquiryReplyInline]                                  # 답변 인라인 표시
    fieldsets = (
        (None, {
            'fields': ('user', 'title', 'content', 'status', 'created_at')
        }),
    )
    # 관리자에서 title 클릭 시 상세 이동, 답변 인라인 관리 가능

@admin.register(InquiryReply)
class InquiryReplyAdmin(admin.ModelAdmin):
    list_display = ('id', 'inquiry', 'admin', 'created_at')
    search_fields = ('inquiry__title', 'content', 'admin__nickname')
    readonly_fields = ('created_at',)
