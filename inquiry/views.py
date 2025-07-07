from django.shortcuts import render

# Create your views here.
def user_support(request):
    return render(request, 'user_support.html')

def inquiry_write(request):
    return render(request, 'inquiry_write.html')