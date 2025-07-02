
from django.shortcuts import render

# Create your views here.
def login(request):
    return render(request,'login.html')

def lgfor(request):
    return render(request,'login_forgot.html')

def signup1(request):
    return render(request,'signup1_terms.html')

def signup2(request):
    return render(request,'signup2_account.html')

def signup3(request):
    return render(request,'signup3_verification.html')
