from django.shortcuts import render, redirect
from inquiry.models import Inquiry
from django.core.paginator import Paginator, EmptyPage
from django.http import JsonResponse


# Create your views here.
def user_support(request):
    inquiries = Inquiry.objects.all().order_by('-created_at')
    paginator = Paginator(inquiries, 10)  # 페이지당 10개
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {"inquiries":page_obj, 'session_user_id': request.session.get('user_id', '')}
    return render(request, 'user_support.html', context)

def my_posts(request):
    user_id = request.session.get('user_id')
    inquiries = Inquiry.objects.filter(user__user_id=user_id).prefetch_related('replies', 'user')

    data = []
    for inquiry in inquiries:
        reply = inquiry.replies.first()  
        data.append({
            'id': inquiry.id,
            'title': inquiry.title,
            'content': inquiry.content,
            'status': inquiry.status,
            'created_at': inquiry.created_at.isoformat(),
            'user__nickname': inquiry.user.nickname if inquiry.user else "탈퇴한 회원입니다",
            # 없을 때
            'answer': reply.content if reply else "아직 답변이 등록되지 않았습니다.",
            # 디테일하게 수정할 때
            'admin_nickname': reply.admin.nickname if reply and reply.admin else "관리자 미표시",
            'answer_created_at': format(reply.created_at, 'Y-m-d H:i') if reply else "작성일 없음"
        })

    return JsonResponse({'inquiries': data})

def all_posts(request):
    inquiries = Inquiry.objects.select_related('user').prefetch_related('replies').order_by('-created_at')

    data = []
    for inquiry in inquiries:
        reply = inquiry.replies.first()
        data.append({
            'title': inquiry.title,
            'content': inquiry.content,
            'status': inquiry.status,
            'created_at': inquiry.created_at.isoformat(),
            'user__nickname': inquiry.user.nickname if inquiry.user else "탈퇴한 회원입니다",
            'answer': reply.content if reply else "아직 답변이 등록되지 않았습니다.",
        })

    return JsonResponse({'inquiries': data})
    

def inquiry_write(request):
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        Inquiry.objects.create(
            user=request.user,
            title=title,
            content=content,
            status='waiting',
        )
        return redirect('/inquiry/support/')  # 문의글 목록 페이지 URL 이름
    else:
        return render(request, 'inquiry_write.html')
        
    
