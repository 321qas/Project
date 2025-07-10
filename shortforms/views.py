from django.shortcuts import render
from shortforms.models import ShortForm, ShortFormImage
from tags.models import Tag

def upload(request):
    return render(request,'shortforms/shorts_upload.html')

def list(request):
    return render(request,'shortforms/shorts_fest_list.html')
   
def search(request):
    return render(request)