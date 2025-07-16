from django.shortcuts import render, get_object_or_404
from .models import Festival, FestivalImage
from django.db.models import Prefetch, Avg, Count
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from reviews.models import Review
from datetime import date
from wishlist.models import Wishlist
from accounts.models import User
from .models import Festival


def view(request, id):  # 축제 상세 페이지
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

    # ★ (1) 위시리스트 개수와 내 위시리스트 상태
    total_wishlist_count = Wishlist.objects.filter(festival=qs).count()
    is_wishlisted = False
    if is_logged_in:
        try:
            user = User.objects.get(user_id=request.session['user_id'])
            user_wishlist_count = Wishlist.objects.filter(user=user).count()
            is_wishlisted = Wishlist.objects.filter(user=user, festival=qs).exists()
        except User.DoesNotExist:
            user = None  # 비정상 세션
    else:
        user = None

    avg_rating = Review.objects.filter(festival=qs).aggregate(avg=Avg('rating'))['avg']
    review_count = Review.objects.filter(festival=qs).count()

    # ----------- 현재 및 축제 날짜 계산 부분 -----------
    today = date.today()
    start = qs.start_date if isinstance(qs.start_date, date) else qs.start_date.date()
    end = qs.end_date if isinstance(qs.end_date, date) else qs.end_date.date()
    if start > today:
        status_text = "Coming Soon"
    elif end < today:
        status_text = "Finished"
    else:
        status_text = "Happening Now"
    # ------------------------------------------

    content = {
        'list': qs,
        'tags': tags_list,
        'is_logged_in': is_logged_in,
        'avg_rating': avg_rating,      # None or float
        'review_count': review_count,  # 0 이상 int
        'status_text': status_text,
        'total_wishlist_count': total_wishlist_count,
        'is_wishlisted': is_wishlisted,
        # (필요시 user도 넘겨줄 수 있음)
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
    name_query = request.GET.get('name', '') 

    festival_qs = Festival.objects.all().order_by('?').prefetch_related(
        Prefetch(
            'images',
            queryset=FestivalImage.objects.order_by('uploaded_at'),
            to_attr='sorted_images'
        ),
        'tags' 
    )

    # 필터링 조건 적용
    if name_query: festival_qs = festival_qs.filter(name__icontains=name_query)
    if region: festival_qs = festival_qs.filter(region__icontains=region)
    if start_date_str: festival_qs = festival_qs.filter(start_date__gte=start_date_str)
    if end_date_str: festival_qs = festival_qs.filter(end_date__lte=end_date_str)

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


# --------------- 위시리스트 통계 차트 -------------------
def Statistics_chart(request):
    # 지역별 위시리스트 카운트
    region_counts = (
        Wishlist.objects.values('festival__region')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    region_labels = dict(Festival.REGION_CHOICES)
    region_interests = []
    for obj in region_counts:
        region_code = obj['festival__region']
        region_interests.append(type('Obj', (), {
            "region": region_code,
            "count": obj["count"]
        })())

    # 축제별 위시리스트 카운트
    festival_counts = (
        Wishlist.objects.values('festival__id', 'festival__name')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    festival_interests = []
    for obj in festival_counts:
        festival_interests.append(type('Obj', (), {
            "festival_id": obj['festival__id'],
            "festival_name": obj['festival__name'],
            "count": obj["count"]
        })())

    return render(request, "festival/Statistics_chart.html", {
        "region_interests": region_interests,
        "region_labels": region_labels,
        "festival_interests": festival_interests,
    })