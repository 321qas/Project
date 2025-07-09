from django.shortcuts import render, get_object_or_404
from .models import Festival, RegionInterest,FestivalImage
from django.db.models import Prefetch, F
from django.http import JsonResponse
import json

def festival_detail(request, pk):
    # 해당 축제의 상세 페이지 접속 빈도를 지역카운트로 반환하는 로직
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

def view(request,id):
    qs = get_object_or_404(
    Festival.objects.prefetch_related(
    Prefetch(
        'images',
        queryset=FestivalImage.objects.order_by('uploaded_at') # 이미지를 업로드된 시간 순으로 정렬
    )),
    id=id)

    tags_list = [{'name': tag.name} for tag in qs.tags.all()]
    content = {'list':qs,'tags': tags_list}
    return render(request, 'festival/view.html', content)

def list(request):
    qs = Festival.objects.all().order_by('?')
    content = {'list': qs}
    return render(request, 'festival/fest_list.html', content)

def search(request):
    region = request.GET.get('region')
    start_date_str = request.GET.get('startDate')
    end_date_str = request.GET.get('endDate')

    festival_qs = Festival.objects.all().order_by('?').prefetch_related(
        Prefetch(
            'images',
            queryset=FestivalImage.objects.order_by('uploaded_at'), # 각 축제별 이미지들을 업로드 일시 순으로 정렬
            to_attr='sorted_images' # 각 Festival 객체에 'sorted_images'라는 속성으로 관련 이미지 리스트가 할당됩니다.
        )
    )

    if region:
        festival_qs = festival_qs.filter(region=region)
    if start_date_str:
        festival_qs = festival_qs.filter(start_date__gte=start_date_str)
    if end_date_str:
        festival_qs = festival_qs.filter(end_date__lte=end_date_str)

    festival_data = []
    for festival in festival_qs:
        first_festival_image = festival.sorted_images[0] if festival.sorted_images else None

        image_url = first_festival_image.image.url if first_festival_image and first_festival_image.image else None

        festival_data.append({
            'id': festival.id,
            'name': festival.name,
            'region': festival.region,
            'start_date': festival.start_date.strftime('%Y-%m-%d') if festival.start_date else None,
            'end_date': festival.end_date.strftime('%Y-%m-%d') if festival.end_date else None,
            'image': image_url,
        })

    return JsonResponse(festival_data, safe=False)