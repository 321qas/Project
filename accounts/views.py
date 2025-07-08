from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User
from tags.models import Tag
from .utils import send_gmail
from django.conf import settings
import uuid

# 1. 로그인 화면
def login(request):
    return render(request, 'login.html')


# 2. 아이디/비밀번호 찾기 화면
def lgfor(request):
    return render(request, 'login_forgot.html')


# 3. 회원가입 Step1: 약관 동의 화면 및 동의 확인
def signup_terms(request):
    """
    - 회원가입 첫 단계: 약관/개인정보 등 필수 약관 동의 여부 체크
    - 필수 동의가 모두 OK일 때만 다음 단계로 이동 (세션 플래그 저장)
    """
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
    """
    - 회원가입 두 번째 단계: ID, 비번, 닉네임, 이메일, 관심태그 등 정보 입력
    - 필수 정보/중복 여부/비밀번호 일치 등 유효성 검사
    - OK시, 세션에 회원 정보 저장 후 이메일 인증 단계로 이동
    """
    if not request.session.get('signup_terms'):
        return redirect('accounts:signup_terms')
    if request.method == "POST":
        user_id = request.POST.get('id')
        password = request.POST.get('password')
        password2 = request.POST.get('confirm-password')
        real_name = request.POST.get('name')
        nickname = request.POST.get('nickname')
        email = request.POST.get('email')
        gender = request.POST.get('gender')
        dob = request.POST.get('dob')
        tag_names = request.POST.getlist('tags')
        # 필수 정보/중복/비밀번호 일치 체크
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
        # 이메일 인증 토큰 발급 & 세션에 정보 저장
        email_token = str(uuid.uuid4())
        request.session['signup_data'] = {
            'user_id': user_id,
            'password': password,
            'real_name': real_name,
            'nickname': nickname,
            'email': email,
            'gender': gender,
            'dob': dob,
            'tags': tag_names,
            'email_token': email_token,
        }
        return redirect('accounts:signup_verify')
    return render(request, 'signup2_account.html')

# 5. 회원가입 Step3: 이메일 인증 안내 및 실제 인증 메일 발송
def signup_verify(request):
    """
    - 이메일 인증 단계(가입 완료 직전)
    - POST로 들어오면 인증 메일 전송 (Gmail API 활용)
    - 사용자는 받은 메일의 인증 링크를 클릭해야 진짜 가입 완료!
    """
    signup_data = request.session.get('signup_data')
    if not signup_data:
        return redirect('accounts:signup_account')
    if request.method == "POST":
        user_email = signup_data['email']
        token = signup_data['email_token']
        verify_url = f"{settings.SITE_URL}/accounts/verify-email/?token={token}&email={user_email}"
        subject = "FastFest 이메일 인증"
        html = f"""
            <h2>FastFest 이메일 인증</h2>
            <p>아래 버튼을 눌러 이메일 인증을 완료하세요.</p>
            <a href="{verify_url}" style="padding:10px 20px; background:#2563eb; color:white; border-radius:5px; text-decoration:none;">이메일 인증하기</a>
        """
        send_gmail(user_email, subject, html)
        messages.info(request, "입력하신 이메일로 인증 메일을 전송했습니다. 이메일에서 인증을 완료하세요.")
        return render(request, 'signup3_verification.html')
    return render(request, 'signup3_verification.html')

# 6. (이메일 링크 클릭시) 실제 회원가입 DB 저장 및 가입 완료 처리
def verify_email(request):
    """
    - 인증 메일의 링크 클릭 시 호출되는 뷰
    - 세션의 토큰/이메일과 URL 파라미터가 일치하면 User DB에 저장
    - 가입 완료 안내 후 로그인 페이지로 이동
    """
    token = request.GET.get('token')
    email = request.GET.get('email')
    signup_data = request.session.get('signup_data')
    if signup_data and signup_data.get('email_token') == token and signup_data.get('email') == email:
        user = User.objects.create_user(
            user_id=signup_data['user_id'],
            email=signup_data['email'],
            password=signup_data['password'],
            real_name=signup_data['real_name'],
            nickname=signup_data['nickname']
        )
        tag_names = signup_data.get('tags', [])
        for tag_name in tag_names:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            user.interest_tags.add(tag)
        user.save()
        request.session.flush()
        messages.success(request, "이메일 인증이 완료되었습니다. 로그인 해주세요.")
        return redirect('accounts:login')
    else:
        messages.error(request, "인증 링크가 잘못되었거나 만료되었습니다.")
        return redirect('accounts:signup_account')
