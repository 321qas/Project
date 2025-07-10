from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.hashers import check_password
from .models import User, EmailVerification
from .utils import send_gmail
from tags.models import Tag
import uuid, datetime, random, string

# 0. 로그인 화면
def login(request):
    if request.method == "POST":
        user_id = request.POST.get('id')
        password = request.POST.get('password')

        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            messages.error(request, "존재하지 않는 ID입니다.")
            return render(request, 'login.html')

        # 비밀번호 검증 (해시 비교)
        if not check_password(password, user.password):
            messages.error(request, "비밀번호가 일치하지 않습니다.")
            return render(request, 'login.html')

        # 로그인 성공: 세션에 정보 저장 (필요에 따라)
        request.session['user_id'] = user.user_id
        request.session['nickname'] = user.nickname
        return redirect('index')

    return render(request, 'login.html')

# 1. 로그아웃
def logout(request):
    request.session.flush()
    return redirect('index')

# 2. 아이디/비밀번호 찾기 화면
def find_id(request):
    user_id = None
    email_entered = None
    not_found = False

    if request.method == "POST":
        email_entered = request.POST.get('email')
        try:
            user = User.objects.get(email=email_entered)
            user_id = user.user_id
            # 2, 3번째 글자를 *로 마스킹
            if len(user_id) >= 3:
                masked_id = (
                    user_id[0]
                    + '*' * (min(2, len(user_id)-1))
                    + user_id[3:]
                )
                if len(user_id) >= 3:
                    masked_id = user_id[0] + '**' + user_id[3:]
                elif len(user_id) == 2:
                    masked_id = user_id[0] + '*'
                else:
                    masked_id = user_id[0]
            else:
                masked_id = user_id  # 1글자 아이디는 그대로 노출
        except User.DoesNotExist:
            not_found = True
            masked_id = None

        return render(request, 'find_id.html', {
            'masked_id': masked_id,
            'email_entered': email_entered,
            'not_found': not_found,
        })

    return render(request, 'find_id.html')

def generate_temp_password(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def find_password(request):
    context = {}
    if request.method == "POST":
        user_id = request.POST.get('user_id')
        email = request.POST.get('email')
        context['user_id_entered'] = user_id
        context['email_entered'] = email

        try:
            user = User.objects.get(user_id=user_id, email=email)
        except User.DoesNotExist:
            context['not_found'] = True
            return render(request, 'find_password.html', context)

        # 임시 비밀번호 생성 & 저장
        temp_pw = generate_temp_password()
        user.set_password(temp_pw)
        user.save()

        # 메일 발송 (Gmail API 활용)
        subject = "FastFest Temporary Password"
        html = f"""
          <div style="max-width:480px;margin:0 auto;padding:40px 24px 28px 24px;background:#fff;border-radius:16px;border:1.5px solid #f97316;font-family:Arial,sans-serif;box-shadow:0 6px 32px #f9731622;">
            <div style="text-align:center;margin-bottom:24px;">
              <h2 style="color:#f97316;margin:0;">FastFest Password Reset</h2>
            </div>
            <p style="font-size:1.08rem;color:#222;margin-bottom:22px;">
              Hello,<br>
              A request to reset your FastFest password was received.<br>
              Your temporary password is below.
            </p>
            <div style="background:#fff7ed;padding:18px 20px;margin:30px 0 28px 0;text-align:center;border-radius:7px;border:1.5px solid #f97316;font-size:1.23rem;letter-spacing:2px;font-weight:bold;color:#d97706;">
              {temp_pw}
            </div>
            <p style="font-size:1.08rem;color:#555;text-align:center;">
              Please <b>log in</b> with the above password,<br>
              and change it immediately for your account's security.
            </p>
            <div style="text-align:center;margin:34px 0 0 0;">
              <a href="https://yourdomain.com/accounts/login/"
                 style="display:inline-block;padding:13px 34px;font-size:1.08rem;background:#f97316;color:#fff;border-radius:7px;text-decoration:none;font-weight:bold;letter-spacing:1px;box-shadow:0 2px 6px #f9731633;">
                 🔒 Go to Login
              </a>
            </div>
            <div style="margin:32px 0 18px 0;">
              <p style="font-size:0.97rem;color:#888;text-align:center;">
                If you did not request a password reset, please ignore this email.<br>
                For help, contact: <b>support@fastfest.com</b>
              </p>
            </div>
            <hr style="margin:28px 0 12px 0;border:none;border-top:1px solid #ffe7c2;">
            <div style="font-size:0.88rem;color:#aaa;text-align:center;">
              © 2025 FastFest<br>
            </div>
          </div>
        """

        send_gmail(email, subject, html)

        context['sent_success'] = True
        return render(request, 'find_password.html', context)

    return render(request, 'find_password.html')


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
<<<<<<< HEAD
=======
    
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
    
>>>>>>> b7ca45e6c1e210ec3837f2d78292a0b9f9f509f9

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
          <div style="max-width:480px;margin:0 auto;padding:40px 24px 28px 24px;background:#fff;border-radius:16px;border:1.5px solid #2563eb;font-family:Arial,sans-serif;box-shadow:0 6px 32px #2563eb22;">
            <div style="text-align:center;margin-bottom:24px;">
              <h2 style="color:#2563eb;margin:0;">FastFest 이메일 인증</h2>
            </div>
            <p style="font-size:1.08rem;color:#222;margin-bottom:22px;">
              안녕하세요!<br>
              FastFest에 회원가입해 주셔서 감사합니다.<br>
              안전한 서비스 이용을 위해 이메일 인증이 필요합니다.<br>
            </p>
            <p style="text-align:center;margin:40px 0;">
              <a href="{verify_url}"
                 style="display:inline-block;padding:14px 36px;font-size:1.1rem;background:#2563eb;color:#fff;border-radius:7px;text-decoration:none;font-weight:bold;letter-spacing:1px;box-shadow:0 2px 6px #2563eb33;">
                 ✉️ 이메일 인증하기
              </a>
            </p>
            <div style="margin:30px 0 18px 0;">
              <p style="font-size:0.98rem;color:#555;">위 버튼이 작동하지 않으면 아래 링크를 복사해 브라우저에 붙여넣어 주세요:</p>
              <div style="background:#f1f5fb;padding:10px 15px;font-size:0.95rem;word-break:break-all;border-radius:4px;color:#2563eb;">{verify_url}</div>
            </div>
            <p style="font-size:0.95rem;color:#888;margin-top:18px;">
              본 메일은 FastFest 회원가입을 위한 이메일 인증입니다.<br>
              본인이 요청하지 않았다면 이 메일을 무시해 주세요.
            </p>
            <hr style="margin:28px 0 12px 0;border:none;border-top:1px solid #e5e7eb;">
            <div style="font-size:0.88rem;color:#aaa;text-align:center;">
              © 2025 FastFest<br>
              문의: support@fastfest.com
            </div>
          </div>
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

# 7. login_password_reset.html >> lgfor에서 메일 발송하면, 발송된 메일의 링크로만 넘어올 수 있음.
def pw_reset(request):
    return render(request, 'login_password_reset.html')