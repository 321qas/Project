from django.shortcuts import render
from shortforms.models import ShortForm, ShortFormImage
from django.http import JsonResponse
from tags.models import Tag
from festivals.models import Festival,FestivalImage
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db import transaction
from django.core.exceptions import ValidationError

def upload(request):
    return render(request,'shortforms/shorts_upload.html')

def create(request):
    try:
        with transaction.atomic(): 
            # 1. 폼 데이터 추출 및 초기 검증
            title = request.POST.get('title')
            festival_name = request.POST.get('festival_name')
            frame_color = request.POST.get('frame_color')
            # tags_string = request.POST.get('tags') # 태그 데이터는 이제 받지 않습니다.

            # 필수 입력 필드 확인 (태그 제외)
            if not all([title, festival_name]): 
                return JsonResponse({'message': '제목과 축제명은 필수 입력 사항입니다.'}, status=400)
            
            # 제목 길이 제한 (50자)
            if len(title) > 50:
                return JsonResponse({'message': '제목은 50자 이내로 입력해주세요.'}, status=400)

            # 2. 축제 객체 찾기
            try:
                current_festival = get_object_or_404(Festival, name=festival_name)
            except Exception: 
                return JsonResponse({'message': f"'{festival_name}' 에 해당하는 축제를 찾을 수 없거나 유효하지 않습니다. 정확한 축제명을 확인해주세요."}, status=400)
            
            # 3. ShortForm 객체 생성
            new_shortform = ShortForm.objects.create(
                title=title,
                festival=current_festival,
                frame_color=frame_color,
                # user=request.user if request.user.is_authenticated else None 
            )

            # 4. 태그 처리 (이 부분은 이전 요청에 따라 제거된 상태입니다.)

            # **5. 이미지 파일 처리 및 유효성 검사 - 이 부분 복구됨**
            uploaded_images = [] 

            for i in range(6): # 클라이언트에서 최대 6개의 이미지를 보낼 수 있으므로 순회
                image_file = request.FILES.get(f'image_{i}')
                if image_file:
                    uploaded_images.append(image_file)
            
            # 이미지 개수 유효성 검사 (클라이언트와 동일하게 최소 1장, 최대 5장)
            if not uploaded_images:
                raise ValidationError("최소 1장의 이미지를 등록해야 합니다.")
            if len(uploaded_images) > 5:
                raise ValidationError("이미지는 최대 5장까지만 등록할 수 있습니다.")

            # 유효성 검사를 통과한 이미지들을 저장합니다.
            for img_file in uploaded_images:
                ShortFormImage.objects.create(
                    shortform=new_shortform,
                    image=img_file
                )

            return JsonResponse({'message': '쇼츠가 성공적으로 생성되었습니다.', 'shortform_id': new_shortform.id}, status=201)

    except ValidationError as e:
        error_message = e.message if hasattr(e, 'message') else ", ".join(e.messages)
        return JsonResponse({'message': f'데이터 유효성 검사 실패: {error_message}'}, status=400)
    
    except Exception as e:
        print(f"create_shortform 처리 중 서버 오류 발생: {e}") 
        return JsonResponse({'message': f'쇼츠 생성 중 알 수 없는 오류가 발생했습니다: {str(e)}'}, status=500)
    
    return JsonResponse({'message': '잘못된 요청 방식입니다.'}, status=405)

def list(request):
    qs = Festival.objects.all().order_by('?')
    try:
        all_tags_objects = Tag.objects.filter(festivals__in=qs).distinct()
    except RecursionError as e:
        print(f"Error at all_tags_objects query: {e}")
        # 오류 발생 시 빈 리스트로 처리하거나, 다른 디버깅 로직 추가
        all_tags_objects = []

    # 2. 각 태그 객체에서 'name' 속성만 추출하여 리스트에 저장
    extracted_tag_names = []
    try:
        for tag_obj in all_tags_objects:
            extracted_tag_names.append(tag_obj.name) # 여기서 오류가 난다면, Tag.__str__이 간접 호출되었을 가능성
    except RecursionError as e:
        print(f"Error during tag name extraction loop: {e}")
        extracted_tag_names = [] # 오류 발생 시 빈 리스트로 처리

    content = {'list': qs, 'tags': extracted_tag_names}
    return render(request, 'shortforms/shorts_fest_list.html', content)

def search(request):
    search_query = request.GET.get('name', '')
    tag_query = request.GET.get('tag', '')
    festivals = Festival.objects.all().prefetch_related('tags', 'images')
    
    if search_query:
        festivals = festivals.filter(name__icontains=search_query)
        
    if tag_query:
        # tag__name__iexact는 Tag 모델의 name 필드가 tag_query와 정확히 일치하는지 (대소문자 구분 없음) 확인합니다.
        # related_name이 'tags'로 되어있다면 이렇게 접근합니다.
        festivals = festivals.filter(tags__name__iexact=tag_query)
        # 또는, 태그가 여러 개 선택될 가능성이 있다면 in을 사용할 수도 있습니다.
        # festivals = festivals.filter(tags__name__in=[tag_query])

    festival_data = []
    for festival in festivals:
        tags_list = [tag.name for tag in festival.tags.all()]

        first_image_url = None
        if festival.images.exists():
            first_image_url = request.build_absolute_uri(festival.images.first().image.url)
        festival_data.append({
            'id': festival.id,
            'name': festival.name,
            'tags': tags_list,
            'image_url': first_image_url, # 여기에 이미지 URL 추가     
        })

    return JsonResponse(festival_data, safe=False, json_dumps_params={'ensure_ascii': False})