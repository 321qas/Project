from django.shortcuts import render, get_object_or_404
from .models import Festival, RegionInterest,FestivalImage
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
    qs = Festival.objects.get(id=id)
    content = {'list':qs}
    return render(request, 'festival/view.html', content)

def list(request):
    qs = Festival.objects.all()
    festival_data = []
    for festival in qs:
        festival_data.append({
            'id': festival.id,
            'name': festival.name,
    })
    json_string_data = json.dumps(festival_data, ensure_ascii=False)
    content = {
        'json_fest_data': json_string_data# JSON 문자열을 템플릿으로 전달
    }
    return render(request, 'festival/fest_list.html', content)
