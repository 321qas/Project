from django.shortcuts import render
from django.http import JsonResponse
from festivals.models import Festival,FestivalImage
from django.db.models import Prefetch
from tags.models import Tag

def index(request):
    return render(request,'index.html')

def jlist(request):
    qs = Festival.objects.filter(
        tags__name='Spring').order_by('?').prefetch_related(
        Prefetch(
            'images',
            queryset=FestivalImage.objects.order_by('uploaded_at'),
            to_attr='sorted_images'
        )
    )[:8]
    
    festival_data = []
    for festival in qs:
        # 1. 첫 번째 이미지 URL 가져오기
        first_festival_image = festival.sorted_images[0] if festival.sorted_images else None
        image_url = first_festival_image.image.url if first_festival_image and first_festival_image.image else None

        festival_data.append({
            'id': festival.id,
            'name': festival.name,
            'region': festival.region,
            'start_date': festival.start_date.strftime('%Y-%m-%d') if festival.start_date else None,
            'end_date': festival.end_date.strftime('%Y-%m-%d') if festival.end_date else None,
            'image': image_url,
            'tag' : 'spring'
        })
        
    print(festival_data)
    return JsonResponse(festival_data, safe=False)