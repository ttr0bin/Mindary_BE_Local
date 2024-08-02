from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from records.models import Record
from records.serializers import RecordSerializer
from datetime import datetime, date

"""
긴 글 작성 플로우
    1. 긴 글 모드에서 작성하기 누르기 -> "카테고리를 선택하세요"
    2. 원하는 카테고리 선택 후 다음 단계를 눌러 긴 글 작성 창이 나옴 - /mindary/records?date=today(oooo-oo-oo)
    3. 이 상태에서 글을 작성하고 POST를 통해 긴 글 등록
"""

@api_view(['POST'])
def record_mode(request):
    date_query_param = request.GET.get('date', None)
    if not date_query_param:
        return Response({"error": "쿼리 파라미터가 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
            
    try:     # 이때 date는 디비에 있는 데이터의 created_at과 비교 할 날짜
        selected_date = datetime.strptime(date_query_param, "%Y-%m-%d").date()
    except ValueError:
        return Response({"error": "쿼리 파라미터 형식을 지켜주세요. YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)
            
    today = date.today()
    if selected_date != today:
        return Response({"error": "오늘의 하루는 오늘 날짜에 기록해보아요!"}, status=status.HTTP_400_BAD_REQUEST)
    record_serializer = RecordSerializer(data=request.data)
    if record_serializer.is_valid():
        record_serializer.save(writer_id = request.user.id)
        return Response(record_serializer.data, status=status.HTTP_201_CREATED)
    return Response(record_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# archive : 긴 글 모아보기
@api_view(['GET'])
def archive(request):
    # 쿼리 파라미터로 필터링 옵션 받기
    filter_liked    = request.GET.get('liked', None)
    order_by_date   = request.GET.get('order_by', None)
    category        = request.GET.get('category', None)
    keyword         = request.GET.get('keyword', None)

    # 레코드 쿼리셋 필터링 및 정렬
    records = Record.objects.filter(writer = request.user)
    if category:
        records = records.filter(category=category)
    if filter_liked == 'true':   # 좋아요한 글만 필터링
        records = records.filter(liked=True)
    if keyword:
        records = records.filter(title__icontains=keyword)
    if order_by_date == 'desc':   # 최신순
        records = records.order_by('-created_at')
    else:
        records = records.order_by('created_at')

    record_serializer = RecordSerializer(records, many=True)
    return Response(record_serializer.data, status=status.HTTP_200_OK)


# 긴글 수정
@api_view(['PATCH'])
def record_detail(request, id):
    date_query_param = request.GET.get('date', None)
    if not date_query_param:
        return Response({"error": "쿼리 파라미터가 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
    
    try:     # 이때 date는 디비에 있는 데이터의 created_at과 비교 할 날짜
        selected_date = datetime.strptime(date_query_param, "%Y-%m-%d").date()
    except ValueError:
        return Response({"error": "쿼리 파라미터 형식을 지켜주세요. YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)
    
    today = date.today()
    if selected_date != today:
        return Response({"error": "오늘의 기록만 수정 할 수 있어요!"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        record = Record.objects.get(id=id)
    except Record.DoesNotExist:
        return Response({"error": "작성한 글이 없습니다!"}, status=status.HTTP_404_NOT_FOUND)
    
    data = request.data
    if 'title' not in data and 'content' not in data and 'liked' not in data:
        return Response({"error": "수정된 것이 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
    
    if 'title' in data:
        record.title = data['title']
    if 'content' in data:
        record.content = data['content']
    if 'liked' in data:
        record.liked = data['liked']
    
    record.edited_at = datetime.now()
    record.save()

    record_serializer = RecordSerializer(record)
    return Response(record_serializer.data, status=status.HTTP_200_OK)
