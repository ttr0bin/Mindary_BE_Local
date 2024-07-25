from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from records.models import Record
from records.serializers import RecordSerializer
from datetime import datetime

# 긴글 모드에서 +을 눌러 긴글 작성 창이 나온 화면 - /mindary/records?date=today(oooo-oo-oo)
# 위의 문장, 내가 잘 이해한 것인지 봐주세요 태경씨
# 이 상태에서 글을 작성하고 POST를 통해 긴글 등록

@api_view(['POST'])
def record_mode(request):
    date_query_param = request.GET.get('date', None)
    if not date_query_param:
        return Response({"error": "쿼리 파라미터가 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
    
    try:     # 이때 date는 디비에 있는 데이터의 created_at과 비교 할 날짜
        date = datetime.strptime(date_query_param, "%Y-%m-%d").date()
    except ValueError:
        return Response({"error": "쿼리 파라미터 형식을 지켜주세요. YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)
    
    today = date.today()
    
    match request.method:
        case 'POST':  # 긴글 POST - 오늘만 가능
            if date != today:
                return Response({"error": "오늘의 하루는 오늘 날짜에 기록해보아요!"}, status=status.HTTP_400_BAD_REQUEST)
            record_serializer = RecordSerializer(data=request.data)
            if record_serializer.is_valid():
                record_serializer.save()
                return Response(record_serializer.data, status=status.HTTP_201_CREATED)
            return Response(record_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
# 긴글 수정
@api_view(['PATCH'])
def record_detail(request, id):
    date_query_param = request.GET.get('date', None)
    if not date_query_param:
        return Response({"error": "쿼리 파라미터가 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
    
    try:     # 이때 date는 디비에 있는 데이터의 created_at과 비교 할 날짜
        date = datetime.strptime(date_query_param, "%Y-%m-%d").date()
    except ValueError:
        return Response({"error": "쿼리 파라미터 형식을 지켜주세요. YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)
    
    today = date.today()
    if date != today:
        return Response({"error": "오늘의 기록만 수정 할 수 있어요!"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        record = Record.objects.get(id=id)
    except Record.DoesNotExist:
        return Response({"error": "작성한 글이 없습니다!"}, status=status.HTTP_404_NOT_FOUND)
    
    data = request.data
    if 'title' not in data and 'content' not in data:
        return Response({"error": "수정된 것이 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
    
    if 'title' in data:
        record.title = data['title']
    if 'content' in data:
        record.content = data['content']
    
    record.edited_at = datetime.now()
    record.save()

    record_serializer = RecordSerializer(record)
    return Response(record_serializer.data, status=status.HTTP_200_OK)