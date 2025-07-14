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
    inquiries = Inquiry.objects.filter(user__user_id=user_id).values(
        'user__nickname', 'title', 'created_at', 'status', 'content'
    )
    data = list(inquiries)
    return JsonResponse({'inquiries': data})
    

def inquiry_write(request):
    return render(request, 'inquiry_write.html')
