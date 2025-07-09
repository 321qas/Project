from django.shortcuts import render
from shortforms.models import ShortForm, ShortFormImage
from tags.models import Tag

def upload(request):
    # form data
    # if request.method == 'POST':
    #     frame_color = request.POST.get('selected_color', 'default')
    #     title = request.POST.get('shorts_title')
    #     festival = request.POST.get('shorts_festname')
    #     user = '축제모아'
    #     name = [tag.strip() for tag in request.POST.get('hiddenTagInput', '').split(',') if tag.strip()]
        
        
        
    #     return render(request,'shortforms/shorts_upload.html')
    # else:
    return render(request,'shortforms/shorts_upload.html')

def list(request):
    return render(request,'shortforms/shorts_fest_list.html')
   
