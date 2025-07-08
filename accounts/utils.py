import base64
from email.mime.text import MIMEText
from googleapiclient.discovery import build
import pickle
import os
from django.conf import settings
# =======================
# Gmail API를 통한 이메일 전송 유틸리티
# =======================

def get_gmail_service():
    """
    Google API에서 발급받은 토큰(token.pickle)로 Gmail 서비스 객체 생성.
    - token.pickle 파일은 최초 인증 후 생성됨 (credentials.json로 인증 → token.pickle 생성)
    - 인증 토큰은 refresh token을 포함하고 있어 만료되어도 자동 연장
    """
    token_path = os.path.join(settings.BASE_DIR, 'accounts', 'Gmail_API', 'token.pickle')
    with open(token_path, 'rb') as token:
        creds = pickle.load(token)
    service = build('gmail', 'v1', credentials=creds)
    return service

def create_message(sender, to, subject, message_text):
    """
    이메일 내용을 Gmail API에서 요구하는 raw 포맷으로 변환.
    - sender: 보내는 사람 이메일 주소 (Gmail API 계정)
    - to: 받을 사람 이메일 주소
    - subject: 이메일 제목
    - message_text: HTML 본문
    """
    message = MIMEText(message_text, 'html')  # HTML형식 메일 생성
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    # Gmail API는 base64로 인코딩된 raw값을 필요로 함
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw_message}

def send_gmail(to, subject, html):
    """
    실제로 이메일을 전송하는 함수.
    - to: 받을 사람 이메일 주소
    - subject: 제목
    - html: 본문 (html 형식)
    """
    service = get_gmail_service()  # Gmail 서비스 객체 준비
    sender = "your.email@gmail.com"  # 이 부분을 본인 Gmail 계정으로 수정!
    message = create_message(sender, to, subject, html)
    # Gmail API에 메일 전송 요청
    send_result = service.users().messages().send(userId="me", body=message).execute()
    return send_result  # 전송 결과(딕셔너리) 반환
