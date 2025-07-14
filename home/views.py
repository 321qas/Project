from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from festivals.models import Festival,FestivalImage
from django.db.models import Prefetch
from tags.models import Tag
from shortforms.models import ShortForm,ShortFormImage
from datetime import datetime

current_datetime = datetime.now()
current_month = current_datetime.month
month_to_season = {
    1: "Winter",
    2: "Winter",
    3: "Spring",
    4: "Spring",
    5: "Spring",
    6: "Summer",
    7: "Summer",
    8: "Summer",
    9: "Autumn",
    10: "Autumn",
    11: "Autumn",
    12: "Winter"
}
season = month_to_season.get(current_month, "잘못된 월")

def index(request):
    try:
        first_shortform = ShortForm.objects.first() # 예시: 첫 번째 쇼츠
    except ShortForm.DoesNotExist:
        first_shortform = None
        
    user_id = request.session.get('user_id')
    nickname = request.session.get('nickname')
    return render(request, 'index.html', {
        'user_id': user_id,
        'nickname': nickname,
        'shortform': first_shortform, # <-- shortform 객체 전달
        'current_sno': first_shortform.id if first_shortform else None,
    })
    
def first(request, sno):
    shortform_obj = get_object_or_404(
        ShortForm.objects.select_related(
            'festival', 'user'
        ).prefetch_related(
            Prefetch('images', queryset=ShortFormImage.objects.order_by('uploaded_at')),
            Prefetch('festival__tags', queryset=Tag.objects.all())
        ),
        id=sno
    )
    context = {
        'shortform': shortform_obj,
        'current_sno': sno, # 현재 보고 있는 쇼츠의 ID를 템플릿에 전달 (JavaScript에서 활용 가능)
    }
    
    return render(request, 'index.html', context)

def jlist(request):
    qs = Festival.objects.filter(
        tags__name=season).order_by('?').prefetch_related(
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
            'tag' : season,
        })
    
    return JsonResponse(festival_data, safe=False)
# 쇼츠 데이터 보내기
def slist(request, sno=None): # sno 매개변수를 추가하고 기본값을 None으로 설정
    
    # 모든 ShortForm 객체를 미리 로드합니다.
    all_shortforms_qs = ShortForm.objects.select_related(
        'festival', 'user'
    ).prefetch_related(
        Prefetch('images', queryset=ShortFormImage.objects.order_by('uploaded_at')),
        Prefetch('festival__tags', queryset=Tag.objects.all())
    )

    ordered_shortforms = []
    
    # sno가 제공되면, 해당 쇼츠를 먼저 찾아서 리스트의 시작에 추가합니다.
    if sno:
        try:
            requested_shortform = all_shortforms_qs.get(id=sno)
            ordered_shortforms.append(requested_shortform)
            # 요청된 쇼츠를 제외한 나머지 쇼츠들을 가져옵니다.
            remaining_shortforms_qs = all_shortforms_qs.exclude(id=sno).order_by('?')
            ordered_shortforms.extend(list(remaining_shortforms_qs)) # 리스트로 변환하여 추가
        except ShortForm.DoesNotExist:
            # sno에 해당하는 쇼츠가 없으면, 전체 쇼츠를 랜덤으로 가져옵니다.
            ordered_shortforms = list(all_shortforms_qs.order_by('?'))
    else:
        # sno가 제공되지 않으면, 전체 쇼츠를 랜덤으로 가져옵니다.
        ordered_shortforms = list(all_shortforms_qs.order_by('?'))

    data = []
    for sf in ordered_shortforms:
        festival_data = None
        if sf.festival:
            tags_list = []
            for tag in sf.festival.tags.all():
                tags_list.append({
                    'id': tag.id,
                    'name': tag.name,
                })
            festival_data = {
                'id': sf.festival.id,
                'name': sf.festival.name,
                'tags': tags_list,
            }

        user_info = {
            'id': sf.user.id,
            'username': sf.user.username,
        } if sf.user else {
            'id': None,
            'username': '탈퇴한 사용자',
        }

        shortform_images_data = []
        for img in sf.images.all():
            shortform_images_data.append({
                'id': img.id,
                'image_url': request.build_absolute_uri(img.image.url),
                'uploaded_at': img.uploaded_at.isoformat(),
            })
        
        data.append({
            'id': sf.id,
            'festival': festival_data,
            'user': user_info,
            'title': sf.title,
            'frame_color': sf.frame_color,
            'image_count': sf.image_count(),
            'images': shortform_images_data,
        })
    return JsonResponse({'shortforms': data}, status=200, safe=False)