from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from .models import User, EmailVerification  # EmailVerification 모델 반드시 import!
from tags.models import Tag
from .utils import send_gmail
from django.conf import settings
import uuid
from django.utils import timezone
import datetime

# 1. 로그인 화면
def login(request):
    return render(request, 'login.html')


# 2. 아이디/비밀번호 찾기 화면
def lgfor(request):
    return render(request, 'login_forgot.html')


# 3. 회원가입 Step1: 약관 동의 화면 및 동의 확인
def signup_terms(request):
    if request.method == "POST":
        terms = request.POST.get('terms')
        privacy = request.POST.get('privacy')
        mandatory = request.POST.get('mandatory')
        if terms != 'agree' or privacy != 'agree' or mandatory != 'agree':
            messages.error(request, "모든 필수 약관에 동의해야 가입할 수 있습니다.")
            return render(request, 'signup1_terms.html')
        request.session['signup_terms'] = True
        return redirect('accounts:signup_account')
    return render(request, 'signup1_terms.html')


# 4. 회원가입 Step2: 기본 정보 입력 화면 및 정보 유효성 검사
def signup_account(request):
    if not request.session.get('signup_terms'):
        return redirect('accounts:signup_terms')

    tags = Tag.objects.all()  # ① 태그 전체 쿼리

    if request.method == "POST":
        user_id = request.POST.get('id')
        password = request.POST.get('password')
        password2 = request.POST.get('confirm-password')
        real_name = request.POST.get('name')
        nickname = request.POST.get('nickname')
        email = request.POST.get('email')
        gender = request.POST.get('gender')
        dob = request.POST.get('dob')
        tag_names = request.POST.getlist('tags')  # ② 선택된 태그 리스트
        tag_ids = request.POST.getlist('tags')

        # 선택된 태그 유지 (폼에 다시 랜더링하기 위해)
        selected_tags = Tag.objects.filter(id__in=tag_ids)
        context = {
            'tags': tags,
            'selected_tags': selected_tags,
        }
        
        if not all([user_id, password, password2, real_name, nickname, email]):
            messages.error(request, "필수 정보를 모두 입력하세요.")
            return render(request, 'signup2_account.html')
        if password != password2:
            messages.error(request, "비밀번호가 일치하지 않습니다.")
            return render(request, 'signup2_account.html')
        if User.objects.filter(user_id=user_id).exists():
            messages.error(request, "이미 존재하는 ID입니다.")
            return render(request, 'signup2_account.html')
        if User.objects.filter(email=email).exists():
            messages.error(request, "이미 존재하는 이메일입니다.")
            return render(request, 'signup2_account.html')
        if User.objects.filter(nickname=nickname).exists():
            messages.error(request, "이미 존재하는 닉네임입니다.")
            return render(request, 'signup2_account.html')

        # 기존 인증정보 삭제(중복 방지)
        EmailVerification.objects.filter(email=email).delete()

        # 이메일 인증 토큰 DB 저장
        email_token = str(uuid.uuid4())
        EmailVerification.objects.create(
            email=email,
            token=email_token,
            user_id=user_id,
            password=password,
            real_name=real_name,
            nickname=nickname,
            gender=gender,
            dob=dob,
            tags=",".join(tag_ids),
            created_at=timezone.now()
        )
        request.session['signup_email'] = email  # 인증대기 이메일 session (OPTIONAL)
        return redirect('accounts:signup_verify')
    
    return render(request, 'signup2_account.html', {
        'tags': tags,
        'selected_tags': []
    })
    
# 프론트엔드 자바스크립트용 실시간 ID 중복 확인 함수
def id_check(request):
    user_id = request.GET.get('id')
    
    if User.objects.filter(user_id=user_id).exists():
        return JsonResponse({'msg': 'id_exist'})
    else:
        return JsonResponse({'msg': 'id_available'})
    
# 프론트엔드 자바스크립트용 실시간 닉네임 중복 확인 함수
def nick_check(request):
    user_nick = request.GET.get('nickname')
    
    if User.objects.filter(nickname=user_nick).exists():
        return JsonResponse({'msg': 'nick_exist'})
    else:
        return JsonResponse({'msg': 'nick_available'})
    
# 프론트엔드 자바스크립트용 실시간 이메일 중복 확인 함수
def mail_check(request):
    user_mail = request.GET.get('email')
    
    if User.objects.filter(email=user_mail).exists():
        return JsonResponse({'msg': 'mail_exist'})
    else:
        return JsonResponse({'msg': 'mail_available'})
    


# 5. 회원가입 Step3: 이메일 인증 안내 및 실제 인증 메일 발송
def signup_verify(request):
    # 세션에서 이메일을 꺼내옴 (최신 가입대기자 기준)
    email = request.session.get('signup_email')
    if not email:
        return redirect('accounts:signup_account')
    try:
        ver = EmailVerification.objects.get(email=email)
    except EmailVerification.DoesNotExist:
        return redirect('accounts:signup_account')

    if request.method == "POST":
        token = ver.token
        verify_url = f"{settings.SITE_URL}/accounts/verify-email/?token={token}&email={email}"
        subject = "FastFest 이메일 인증"
        html = f"""
            <h2>FastFest 이메일 인증</h2>
            <br>
            <p>아래 버튼을 눌러 이메일 인증을 완료하세요.</p>
            <a href="{verify_url}" style="padding:10px 20px; background:#2563eb; color:white; border-radius:5px; text-decoration:none;">이메일 인증하기</a>
        """
        send_gmail(email, subject, html)
        messages.info(request, "입력하신 이메일로 인증 메일을 전송했습니다. 이메일에서 인증을 완료하세요.")
        return render(request, 'signup3_verification.html')
    return render(request, 'signup3_verification.html')


# 6. (이메일 링크 클릭시) 실제 회원가입 DB 저장 및 가입 완료 처리
def verify_email(request):
    token = request.GET.get('token')
    email = request.GET.get('email')
    try:
        ver = EmailVerification.objects.get(email=email, token=token)
    except EmailVerification.DoesNotExist:
        messages.error(request, "인증 링크가 잘못되었거나 만료되었습니다.")
        return render(request, 'signup3_verification.html')

    # 만료여부 검사 (10분)
    if timezone.now() > ver.created_at + datetime.timedelta(minutes=10):
        ver.delete()
        messages.error(request, "인증 링크가 만료되었습니다. 다시 시도해주세요.")
        return render(request, 'signup3_verification.html')

    # 이미 인증된 이메일이면(=User가 존재), 중복 안내
    if User.objects.filter(email=email).exists():
        messages.error(request, "이미 가입된 이메일입니다. 로그인 해주세요.")
        return redirect('accounts:login')

    # User 생성
    user = User.objects.create_user(
        user_id=ver.user_id,
        email=ver.email,
        password=ver.password,
        real_name=ver.real_name,
        nickname=ver.nickname,
        gender=ver.gender,
        dob=ver.dob   
    )
    tag_ids = [tid.strip() for tid in ver.tags.split(',') if tid.strip()]
    # 관심 태그 저장
    for tag_id in tag_ids:
        try:
            tag = Tag.objects.get(id=int(tag_id))
            user.interest_tags.add(tag)
        except Tag.DoesNotExist:
            continue
    user.save()

    ver.delete()
    if 'signup_email' in request.session:
        del request.session['signup_email']
    messages.success(request, "이메일 인증이 완료되었습니다. 로그인 해주세요.")
    return redirect('accounts:login')
