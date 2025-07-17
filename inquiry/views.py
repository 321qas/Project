from django.shortcuts import render, redirect
from inquiry.models import Inquiry
from django.core.paginator import Paginator, EmptyPage
from django.http import JsonResponse
from django.contrib import messages



# Create your views here.
def user_support(request):
    # faq
    keyword = request.GET.get('key', '').strip().lower()
    faq_list = [
    {"question" : "When can I get a refund if I cancel after booking?", "answer" : "If you request a reservation cancellation, a refund will be issued within 2-3 business days. There may be delays depending on the credit card company's circumstances."},
    {"question" : "Is it possible to purchase on-site on the day of the festival?", "answer" : "Yes, you can purchase some tickets on-site. However, since the number is limited, advance reservations are recommended."},
    {"question" : "How do I transfer or refund a ticket?", "answer" : "You can request cancellation on My Page or request a transfer through the customer center."},
    {"question" : "How do I create a festival-related short form?", "answer" : "On the main page with the short form function, you can upload by clicking the (+) button located at the top to the right of the short form."},
    {"question" : "Can short forms only be created with the theme of festivals that exist on the site?", "answer" : "es, when entering the festival title and tag, information about existing festivals is retrieved, so festivals that are not updated are not possible."},
    {"question" : "Does the site work on mobile?", "answer" : "Currently, the mobile version is not supported, but it will be updated in the future."},
    {"question" : "Do you distinguish between free and paid festivals?", "answer" : "This feature is not currently supported."},
    {"question" : "What if I want to recommend a festival that isn't on the site?", "answer" : "If you post a recommended festival through inquiry at the bottom of the customer center page (this is the current page), we will update it after reviewing it."},
    {"question" : "How is short form recommended?", "answer" : "When logging in, it operates using an algorithm based on user interest tags, and for non-members, short forms containing popular tags are recommended."}
    ]
    
    if keyword:
        faq_list = [faq for faq in faq_list
                    if keyword in faq["question"].lower() or keyword in faq["answer"].lower()]


    faq_paginator = Paginator(faq_list, 3)  # 페이지당 3개 FAQ 표시
    faq_page_number = request.GET.get('faq_page', 1)
    faq_page_obj = faq_paginator.get_page(faq_page_number)

    
    
    context = {'session_user_id': request.session.get('user_id', ''), "faq_list": faq_page_obj, "keyword":keyword}
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
        
        
    paginator = Paginator(data, 10)  # 페이지당 10개
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    filtered_data = {
    'inquiries': page_obj.object_list,
    'pagination': {
        'current': page_obj.number,
        'total_pages': paginator.num_pages,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous()
        }
    }
    return JsonResponse(filtered_data)

def all_posts(request):
    inquiries = Inquiry.objects.all().prefetch_related('replies').order_by('-created_at')

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
        
    paginator = Paginator(data, 10)  # 페이지당 10개
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    filtered_data = {
    'inquiries': page_obj.object_list,
    'pagination': {
        'current': page_obj.number,
        'total_pages': paginator.num_pages,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous()
        }
    }
    return JsonResponse(filtered_data)

    
    

def inquiry_write(request):
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content_box')
        # 작성여부
        if not title or not content:
            msg = {'error_msg':'Both title and content should be written',
                   'written_title': title,
                   'written_content': content}
            return render(request, 'inquiry_write.html', {"msg":msg})
    
        # store in db
        Inquiry.objects.create(
            user=request.user,
            title=title,
            content=content,
            status='waiting',
        )
        messages.success(request, 'Thanks for your opinion')
        return redirect('/inquiry/support/')

    else:
        return render(request, 'inquiry_write.html')
        
    
