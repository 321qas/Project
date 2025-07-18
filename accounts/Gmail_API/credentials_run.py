# credentials_run.py
# Gmail API 인증을 위한 스크립트
# 사용법: 터미널에서 python credentials_run.py

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os

# 사용할 권한(스코프)
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def authenticate_gmail():
    creds = None
    token_path = 'token.pickle'

    # 1. 기존 토큰이 있으면 불러오기
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    # 2. 토큰이 없거나, 만료됐거나, refresh 불가하면 새로 인증
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print("토큰 자동 갱신 실패. 재인증을 진행합니다. (사유:", e, ")")
                if os.path.exists(token_path):
                    os.remove(token_path)
                return authenticate_gmail()  # 재귀적으로 다시 실행
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # 3. 인증 후 토큰 저장
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    return creds

if __name__ == "__main__":
    creds = authenticate_gmail()
    print("✅ 인증이 완료되었습니다!")
