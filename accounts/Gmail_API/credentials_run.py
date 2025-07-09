# Gmail API 인증을 위한 스크립트
# 사용법 : 터미널 -> python credentials_run.py 


from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pickle
import os

# 사용할 권한(스코프)
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def authenticate_gmail():
    creds = None
    # 이미 발급된 토큰이 있으면 재사용
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # 없으면 새로 인증
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # 인증 완료 후 토큰 저장
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

if __name__ == "__main__":
    creds = authenticate_gmail()
    print("인증이 완료되었습니다!")
