from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from accounts import views
from accounts import views as accounts_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('festivals/', include('festivals.urls')),
    path('naver/login/start/', accounts_views.naver_login_start, name='naver_login_start'),
    path('naver/callback/', views.naver_callback, name='naver_callback'), # 네이버 로그인 콜백 URL
    path('accounts/', include('accounts.urls')),
    path('inquiry/', include('inquiry.urls')),
    path('shortforms/', include('shortforms.urls')),
    path('api/', include('reviews.urls')),  # 리뷰 관련 API URL 추가
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)