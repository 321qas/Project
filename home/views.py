from django.shortcuts import render
from django.http import JsonResponse
from festivals.models import Festival,FestivalImage
from django.db.models import Prefetch
from tags.models import Tag
from shortforms.models import ShortForm,ShortFormImage

def index(request):
    user_id = request.session.get('user_id')
    nickname = request.session.get('nickname')
    return render(request, 'index.html', {
        'user_id': user_id,
        'nickname': nickname,
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

    return JsonResponse(festival_data, safe=False)
# 쇼츠 데이터 보내기
def slist(request):
    # ShortForm, Festival, User 모델을 미리 로드하고, ShortFormImage와 Festival의 Tag도 미리 로드합니다.
    shortforms = ShortForm.objects.select_related(
        'festival', 'user' # ForeignKey 관계를 JOIN으로 미리 로드
    ).prefetch_related(
        Prefetch('images', queryset=ShortFormImage.objects.order_by('uploaded_at')), # 쇼츠 이미지 미리 로드
        Prefetch('festival__tags', queryset=Tag.objects.all()) # 축제에 연결된 태그들을 미리 로드
    ).order_by('?') # 최신순으로 정렬

    data = []
    for sf in shortforms:
        # 1. 축제 정보 처리 및 태그 포함
        festival_data = None
        if sf.festival:
            # 축제에 연결된 태그 목록 생성 (Prefetch 덕분에 추가 쿼리 없음)
            tags_list = []
            for tag in sf.festival.tags.all():
                tags_list.append({
                    'id': tag.id,
                    'name': tag.name,
                    # Tag 모델에 다른 필드가 있다면 여기에 추가할 수 있습니다.
                })

            festival_data = {
                'id': sf.festival.id,
                'name': sf.festival.name,
                'tags': tags_list, # 축제 태그 목록 추가
            }

        # 2. 사용자 정보 처리 (settings.AUTH_USER_MODEL에 username 필드가 있다고 가정)
        user_info = {
            'id': sf.user.id,
            'username': sf.user.username,
        } if sf.user else {
            'id': None,
            'username': '탈퇴한 사용자',
        }

        # 3. 첨부된 쇼츠 이미지 URL 목록 생성
        shortform_images_data = []
        for img in sf.images.all(): # Prefetch 덕분에 추가 쿼리 없음
            shortform_images_data.append({
                'id': img.id,
                'image_url': request.build_absolute_uri(img.image.url),
                'uploaded_at': img.uploaded_at.isoformat(),
            })
        
        # 최종 쇼츠 데이터를 리스트에 추가
        data.append({
            'id': sf.id,
            'festival': festival_data, # 축제 상세 정보 및 태그 포함
            'user': user_info,
            'title': sf.title,
            'frame_color': sf.frame_color,
            'image_count': sf.image_count(),
            'images': shortform_images_data, # 쇼츠 이미지 정보
        })
        print(data)
    return JsonResponse({'shortforms': data}, status=200, safe=False)