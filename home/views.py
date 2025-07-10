from django.shortcuts import render
from django.http import JsonResponse
from festivals.models import Festival,FestivalImage
from django.db.models import Prefetch
from tags.models import Tag

def index(request):
    user_id = request.session.get('user_id')
    nickname = request.session.get('nickname')
    return render(request, 'index.html', {
        'user_id': user_id,
        'nickname': nickname,
<<<<<<< HEAD
    })

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
    
=======
    })
>>>>>>> b7ca45e6c1e210ec3837f2d78292a0b9f9f509f9
