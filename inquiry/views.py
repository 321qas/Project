from django.shortcuts import render

# Create your views here.
def support(request):
    return render(request,'UserSupport.html')

def write(request):
    return render(request,'inquiry_write.html')