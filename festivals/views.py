from django.shortcuts import render, get_object_or_404
from .models import Festival, RegionInterest,FestivalImage
from django.db.models import Prefetch, F
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from reviews.models import Review
import json

def festival_detail(request, pk): # 해당 축제의 상세 페이지 접속 빈도를 지역카운트로 반환하는 로직
    # 해당 축제 불러오기
    festival = get_object_or_404(Festival, pk=pk)
    # 해당 축제의 지역 코드 추출
    region_code = festival.region

    # 지역별 관심도 카운트 +1   
    region_interest, created = RegionInterest.objects.get_or_create(region=region_code)
    region_interest.count += 1
    region_interest.save(update_fields=["count"])

    # 나머지(상세페이지 렌더링)
    #  return render(request, "festival/detail.html", {"festival": festival})
    
def region_interest_chart(request): # 지역별 관심도 통계 페이지
    region_interests = RegionInterest.objects.all().order_by('-count') # 모든 지역별 관심도 객체(쿼리셋) 가져오기
    region_labels = dict(Festival.REGION_CHOICES) # 한글명 매핑 딕셔너리 생성 (코드→한글)
    return render(request, "festival/region_interest_chart.html", { # 템플릿에 데이터 전달
        "region_interests": region_interests, # 관심도 쿼리셋 (for문에서 사용)
        "region_labels": region_labels        # 코드→한글 매핑 딕셔너리
    })

from reviews.models import Review
from django.db.models import Avg

def view(request, id): # 축제 상세 페이지
    qs = get_object_or_404(
        Festival.objects.prefetch_related(
            Prefetch(
                'images',
                queryset=FestivalImage.objects.order_by('uploaded_at')
            )
        ),
        id=id
    )

    tags_list = [{'name': tag.name} for tag in qs.tags.all()]
    is_logged_in = request.session.get('user_id') is not None

    avg_rating = Review.objects.filter(festival=qs).aggregate(avg=Avg('rating'))['avg']
    review_count = Review.objects.filter(festival=qs).count()

    content = {
        'list': qs,
        'tags': tags_list,
        'is_logged_in': is_logged_in,
        'avg_rating': avg_rating,      # None or float
        'review_count': review_count,  # 0 이상 int
    }
    return render(request, 'festival/view.html', content)



def list(request): # 축제 목록 페이지
    qs = Festival.objects.all().order_by('?')
    content = {'list': qs}
    return render(request, 'festival/fest_list.html', content)

def search(request): # 축제 검색
    region = request.GET.get('region')
    start_date_str = request.GET.get('startDate')
    end_date_str = request.GET.get('endDate')
    # name_query = request.GET.get('name', '') 

    festival_qs = Festival.objects.all().order_by('?').prefetch_related(
        Prefetch(
            'images',
            queryset=FestivalImage.objects.order_by('uploaded_at'),
            to_attr='sorted_images'
        ),
        'tags' 
    )

    # 필터링 조건 적용
    if region: festival_qs = festival_qs.filter(region=region)
    if start_date_str: festival_qs = festival_qs.filter(start_date__gte=start_date_str)
    if end_date_str: festival_qs = festival_qs.filter(end_date__lte=end_date_str)
    
    # 이름 검색 조건 추가
    # if name_query: festival_qs = festival_qs.filter(name__icontains=name_query)

    festival_data = []
    for festival in festival_qs:
        first_festival_image = festival.sorted_images[0] if festival.sorted_images else None
        image_url = request.build_absolute_uri(first_festival_image.image.url) if first_festival_image and first_festival_image.image else None
        tags_list = [tag.name for tag in festival.tags.all()]
        festival_data.append({
            'id': festival.id,
            'name': festival.name,
            'region': festival.region,
            'start_date': festival.start_date.strftime('%Y-%m-%d') if festival.start_date else None,
            'end_date': festival.end_date.strftime('%Y-%m-%d') if festival.end_date else None,
            'image': image_url,
            'tags': tags_list, # 여기에 태그 이름 리스트 추가
        })

    return JsonResponse(festival_data, safe=False)


