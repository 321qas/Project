from django.urls import path,include
from . import views
app_name='accounts'
urlpatterns = [
    path('login/',views.login,name='login'),
    path('lgfor/',views.lgfor,name='lgfor'), 
    path('signup1/',views.signup1,name='signup1'),
    path('signup2/',views.signup2,name='signup2'),
    path('signup3/',views.signup3,name='signup3'),
]