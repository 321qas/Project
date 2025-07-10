from django.shortcuts import render

def index(request):
    user_id = request.session.get('user_id')
    nickname = request.session.get('nickname')
    return render(request, 'index.html', {
        'user_id': user_id,
        'nickname': nickname,
    })