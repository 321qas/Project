from django.shortcuts import render, redirect
from inquiry.models import Inquiry
from django.core.paginator import Paginator, EmptyPage
from django.http import JsonResponse


# Create your views here.
def user_support(request):
    # faq
    keyword = request.GET.get('key', '').strip().lower()
    faq_list = [
    {"question" : "예매 후 취소 시 환불은 언제 되나요?", "answer" : "예매 취소 요청 시 영업일 기준 2~3일 내 환불이 진행됩니다. 카드사 사정에 따라 지연될 수 있습니다."},
    {"question" : "축제 당일 현장 구매도 가능한가요?", "answer" : "네, 현장에서도 일부 티켓 구매가 가능합니다. 다만 수량이 한정되어 있으니 사전 예매를 권장드립니다."},
    {"question" : "티켓 양도나 환불은 어떻게 하나요?", "answer" : "마이페이지에서 취소 요청을 하거나, 고객센터를 통해 양도 신청을 하실 수 있습니다."},
    {"question" : "축제 관련 숏폼은 어떻게 만드나요?", "answer" : "숏폼 기능이 있는 메인페이지에서 숏폼 우측에 가장 상단에 위치한 (+) 버튼을 누르면 업로드 하실 수 있습니다"},
    {"question" : "숏폼은 사이트 내에 존재하는 축제를 주제로만 생성 가능한가요?", "answer" : "네, 축제 제목 및 태그를 입력할 때 존재하는 축제의 정보를 불러오기 때문에 업데이트 되지 않은 축제는 불가능합니다"},
    {"question" : "모바일에서도 사이트가 작동하나요?", "answer" : "현재까지는 모바일 버전을 지원하지 않으나 차후 업데이트 예정입니다"},
    {"question" : "무료/유료 축제를 구별해 주나요?", "answer" : "현재까지는 지원하지 않는 기능입니다"},
    {"question" : "사이트에 없는 축제를 추천하고 싶으면 어떻게 해야 하나요?", "answer" : "고객센터페이지(현재 페이지입니다) 하단에 inquiry에서 추천 축제를 올려드리면 검토 후 업데이트 하겠습니다."},
    {"question" : "숏폼이 추천되는 원리는 어떻게 되나요?", "answer" : "로그인 시에는 사용자 관심 태그 기반 알고리즘으로 작동하며, 비회원에 경우 인기 태그를 포함한 숏폼이 추천됩니다"}
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
        return redirect('/inquiry/support/')  # 문의글 목록 페이지 URL 이름
    else:
        return render(request, 'inquiry_write.html')
        
    
