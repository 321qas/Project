from django.shortcuts import render

def upload(request):
    return render(request,'shortforms/shorts_upload.html')

def list(request):
    return render(request,'shortforms/shorts_fest_list.html')
