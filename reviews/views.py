from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from .models import Review, ReviewImage, Comment
from festivals.models import Festival
from .forms import ReviewForm, CommentForm
from django.shortcuts import get_object_or_404

from django.views.decorators.csrf import csrf_exempt

# 리뷰 목록 조회
def review_list(request, festival_id):
    festival = get_object_or_404(Festival, id=festival_id)
    reviews = Review.objects.filter(festival=festival).select_related('user').prefetch_related('images', 'comments')
    # 로그인 세션 기반으로 owner 판별
    session_user_id = request.session.get('user_id')
    data = []
    for r in reviews:
        data.append({
            'id': r.id,
            'user': r.user.nickname,
            'user_id': r.user.id,
            'is_owner': session_user_id and str(r.user.user_id) == str(session_user_id),
            'rating': r.rating,
            'content': r.content,
            'created_at': r.created_at.strftime("%Y-%m-%d %H:%M"),
            'images': [img.image.url for img in r.images.all()],
            'like_count': r.like_set.count() if hasattr(r, "like_set") else 0,
            'comments': [{
                'id': c.id,
                'user': c.user.nickname,
                'content': c.content,
                'created_at': c.created_at.strftime("%Y-%m-%d %H:%M"),
                'is_owner': session_user_id and str(c.user.user_id) == str(session_user_id),
            } for c in r.comments.all()],
        })
    return JsonResponse({'reviews': data})

# 리뷰 등록
@csrf_exempt
@require_http_methods(["POST"])
def review_create(request, festival_id):
    # 세션 체크
    session_user_id = request.session.get('user_id')
    if not session_user_id:
        return HttpResponseForbidden("로그인 후 이용 가능합니다.")

    festival = get_object_or_404(Festival, id=festival_id)
    from accounts.models import User  # User 모델 import
    try:
        user = User.objects.get(user_id=session_user_id)
    except User.DoesNotExist:
        return HttpResponseForbidden("유효하지 않은 사용자입니다.")

    form = ReviewForm(request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.user = user
        review.festival = festival
        review.save()
        for img in request.FILES.getlist('images'):
            ReviewImage.objects.create(review=review, image=img)
        return JsonResponse({'result': 'ok'})
    else:
        return JsonResponse({'result': 'error', 'errors': form.errors}, status=400)

# 리뷰 삭제
@csrf_exempt
@require_http_methods(["DELETE"])
def review_delete(request, review_id):
    session_user_id = request.session.get('user_id')
    if not session_user_id:
        return HttpResponseForbidden("로그인 후 이용 가능합니다.")
    review = get_object_or_404(Review, id=review_id)
    if str(review.user.user_id) != str(session_user_id):
        return HttpResponseForbidden("권한 없음")
    review.delete()
    return JsonResponse({'result': 'ok'})

# 리뷰 수정
@csrf_exempt
@require_http_methods(["POST"])
def review_update(request, review_id):
    session_user_id = request.session.get('user_id')
    if not session_user_id:
        return HttpResponseForbidden("로그인 후 이용 가능합니다.")
    review = get_object_or_404(Review, id=review_id)
    if str(review.user.user_id) != str(session_user_id):
        return HttpResponseForbidden("권한 없음")
    form = ReviewForm(request.POST, instance=review)
    if form.is_valid():
        form.save()
        return JsonResponse({'result': 'ok'})
    else:
        return JsonResponse({'result': 'error', 'errors': form.errors}, status=400)

# 댓글 등록
@csrf_exempt
@require_http_methods(["POST"])
def comment_create(request, review_id):
    session_user_id = request.session.get('user_id')
    if not session_user_id:
        return HttpResponseForbidden("로그인 후 이용 가능합니다.")
    from accounts.models import User
    try:
        user = User.objects.get(user_id=session_user_id)
    except User.DoesNotExist:
        return HttpResponseForbidden("유효하지 않은 사용자입니다.")
    review = get_object_or_404(Review, id=review_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.user = user
        comment.review = review
        comment.save()
        return JsonResponse({'result': 'ok'})
    else:
        return JsonResponse({'result': 'error', 'errors': form.errors}, status=400)

# 댓글 삭제
@csrf_exempt
@require_http_methods(["DELETE"])
def comment_delete(request, comment_id):
    session_user_id = request.session.get('user_id')
    if not session_user_id:
        return HttpResponseForbidden("로그인 후 이용 가능합니다.")
    comment = get_object_or_404(Comment, id=comment_id)
    if str(comment.user.user_id) != str(session_user_id):
        return HttpResponseForbidden("권한 없음")
    comment.delete()
    return JsonResponse({'result': 'ok'})
