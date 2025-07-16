import random
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from festivals.models import Festival, FestivalImage
from django.db.models import Prefetch
from tags.models import Tag
from shortforms.models import ShortForm, ShortFormImage
from datetime import datetime


# ------------------ 메인 인덱스 페이지 ------------------
def index(request):
    try:
        # 첫 번째 쇼츠 객체 가져오기 (없으면 None)
        first_shortform = ShortForm.objects.first()
    except ShortForm.DoesNotExist:
        first_shortform = None
    
    # 세션에서 유저 정보 읽기
    user_id = request.session.get('user_id')
    nickname = request.session.get('nickname')
    # 인덱스 렌더링 (쇼츠, 유저정보, 현재 쇼츠번호 전달)
    return render(request, 'index.html', {
        'user_id': user_id,
        'nickname': nickname,
        'shortform': first_shortform,
        'current_sno': first_shortform.id if first_shortform else None,
    })
    
# ------------------ 쇼츠 상세페이지 ------------------
def first(request, sno):
    # 주어진 id(sno)에 해당하는 ShortForm 객체와 관련 정보 미리 가져오기
    shortform_obj = get_object_or_404(
        ShortForm.objects.select_related('festival', 'user').prefetch_related(
            Prefetch('images', queryset=ShortFormImage.objects.order_by('uploaded_at')),
            Prefetch('festival__tags', queryset=Tag.objects.all())
        ),
        id=sno
    )
    # 컨텍스트에 쇼츠 객체 및 id 전달
    context = {
        'shortform': shortform_obj,
        'current_sno': sno,
    }
    return render(request, 'index.html', context)

# ------------------ 시즌별 축제 8개 json 리스트 ------------------

def get_season(month): # 계절 계산 함수
    if month in [3, 4, 5]:
        return 'Spring'
    elif month in [6, 7, 8]:
        return 'Summer'
    elif month in [9, 10, 11]:
        return 'Autumn'
    else:
        return 'Winter'

def jlist(request): # 시즌별 축제 8개 json 응답
    current_month = datetime.now().month
    current_season = get_season(current_month)

    # 축제 전체에서 이미지 미리 읽기
    qs = Festival.objects.prefetch_related(
        Prefetch('images', queryset=FestivalImage.objects.order_by('uploaded_at'), to_attr='sorted_images')
    )

    festival_data = []
    for festival in qs:
        # 시작월로 계절 계산
        if not festival.start_date:
            continue
        season = get_season(festival.start_date.month)
        if season != current_season:
            continue

        # 대표이미지 추출
        first_image = festival.sorted_images[0] if festival.sorted_images else None
        image_url = first_image.image.url if first_image and first_image.image else None

        festival_data.append({
            'id': festival.id,
            'name': festival.name,
            'region': festival.region,
            'start_date': festival.start_date.strftime('%Y-%m-%d'),
            'end_date': festival.end_date.strftime('%Y-%m-%d') if festival.end_date else None,
            'image': image_url,
            'tag': season,
        })

    # 8개만 랜덤 추출
    result = random.sample(festival_data, min(8, len(festival_data)))
    return JsonResponse(result, safe=False)


# ------------------ 쇼츠 데이터 json 응답 ------------------

def slist(request, sno=None):
    # 모든 쇼츠(ShortForm) 미리 가져오기
    all_shortforms_qs = ShortForm.objects.select_related('festival', 'user').prefetch_related(
        Prefetch('images', queryset=ShortFormImage.objects.order_by('uploaded_at')),
        Prefetch('festival__tags', queryset=Tag.objects.all())
    )

    ordered_shortforms = []
    # sno가 있으면 해당 쇼츠를 맨 앞에 두고, 나머지는 랜덤
    if sno:
        try:
            requested_shortform = all_shortforms_qs.get(id=sno)
            ordered_shortforms.append(requested_shortform)
            remaining_shortforms_qs = all_shortforms_qs.exclude(id=sno).order_by('?')
            ordered_shortforms.extend(list(remaining_shortforms_qs))
        except ShortForm.DoesNotExist:
            # sno 잘못됐으면 전체 랜덤
            ordered_shortforms = list(all_shortforms_qs.order_by('?'))
    else:
        # sno 없으면 전체 랜덤
        ordered_shortforms = list(all_shortforms_qs.order_by('?'))

    data = []
    for sf in ordered_shortforms:
        # 축제 정보 json화
        festival_data = None
        if sf.festival:
            tags_list = [{'id': tag.id, 'name': tag.name} for tag in sf.festival.tags.all()]
            festival_data = {
                'id': sf.festival.id,
                'name': sf.festival.name,
                'tags': tags_list,
            }

        # 유저 정보
        user_info = {
            'id': sf.user.id,
            'nickname': sf.user.nickname,
        } if sf.user else {
            'id': None,
            'nickname': '탈퇴한 사용자',
        }

        # 이미지 리스트
        shortform_images_data = [{
            'id': img.id,
            'image_url': request.build_absolute_uri(img.image.url),
            'uploaded_at': img.uploaded_at.isoformat(),
        } for img in sf.images.all()]
        
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
