
# 유저의 로그인 여부와 닉네임을 home 템플릿에 전역 변수화 >> 헤더에 사용

def user_info(request):
    if request.user.is_authenticated:
        return {
            'is_login': True,
            'nickname': request.user.nickname
        }
    else:
        return {
            'is_login': False,
        }