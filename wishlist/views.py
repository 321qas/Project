from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Wishlist
from festivals.models import Festival

@login_required
def add_wishlist(request):
    if request.method == "POST":
        fest_id = request.POST.get("festival_id")
        try:
            festival = Festival.objects.get(id=fest_id)
        except Festival.DoesNotExist:
            return JsonResponse({"result": "fail", "error": "Festival not found"})
        
        # 중복 방지
        obj, created = Wishlist.objects.get_or_create(user=request.user, festival=festival)
        if not created:
            # 이미 있으면 삭제(토글)
            obj.delete()
            action = "removed"
        else:
            action = "added"
        
        # **해당 축제의 전체 위시리스트 개수**
        count = Wishlist.objects.filter(festival=festival).count()
        return JsonResponse({"result": "ok", "created": created, "count": count, "action": action})
    return JsonResponse({"result": "fail", "error": "Only POST allowed"})

@login_required
def wishlist_count(request):
    count = Wishlist.objects.filter(user=request.user).count()
    return JsonResponse({"count": count})
