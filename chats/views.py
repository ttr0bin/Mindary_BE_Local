from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, date

from chats.models import Chat
from records.models import Record
from chats.serializers import ChatSerializer
from records.serializers import RecordSerializer

"""
[정리]
* strptime 함수 - "날짜와 시간 형식의 문자열"을 datetime(타입형)으로 변환

* 뒤에 .date()를 붙이냐 안붙이냐의 차이점
    date_time_obj = datetime.strptime("2024-01-01", "%Y-%m-%d")
    print(date_time_obj)  # 출력: 2024-01-01 00:00:00

    date_obj = datetime.strptime("2024-01-01", "%Y-%m-%d").date()
    print(date_obj)  # 출력: 2024-01-01
"""

# 메인화면 - mindary?date=0000-00-00
# 메인화면에서 chat을 POST하거나
# 메인화면에서 GET으로 긴글, 짧은글 모두 반환
@api_view(['GET', 'POST'])
def main_page(request):
    date_query_param = request.GET.get('date', None)
    if not date_query_param:
        return Response({"error": "쿼리 파라미터가 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
    
    try:     # 이때 date는 디비에 있는 데이터의 created_at과 비교 할 날짜
        selected_date = datetime.strptime(date_query_param, "%Y-%m-%d").date()
    except ValueError:
        return Response({"error": "쿼리 파라미터 형식을 지켜주세요. YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)
    
    today = date.today()
    match request.method:
        case 'GET':   # 해당 날짜의 모든 데이터를 GET으로 반환
            chats = Chat.objects.filter(created_at__date=selected_date, writer = request.user)
            records = Record.objects.filter(created_at__date=selected_date)
            
            chat_serializer = ChatSerializer(chats, many=True)
            record_serializer = RecordSerializer(records, many=True)
            
            response_data = {
                "chats": chat_serializer.data,
                "records": record_serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        case 'POST':  # 채팅 POST - 오늘만 가능
            if selected_date != today:
                return Response({"error": "오늘의 하루는 오늘 날짜에 기록해보아요!"}, status=status.HTTP_400_BAD_REQUEST)
            serializer = ChatSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(writer_id = request.user.id)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 채팅 삭제 기능 - 채팅은 카톡처럼 별도의 수정 없이 삭제만 가능하도록 구현해봤음.
# 글 id에 맞춰서 삭제해야 하므로, 별도의 url pattern을 설정하고, 그렇기 때문에 별도의 함수로 구현
@api_view(['DELETE'])
def chat_detail(request, id):
    date_query_param = request.GET.get('date', None)
    if not date_query_param:
        return Response({"error": "쿼리 파라미터가 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
    
    try:     # 이때 date는 디비에 있는 데이터의 created_at과 비교 할 날짜
        selected_date = datetime.strptime(date_query_param, "%Y-%m-%d").date()
    except ValueError:
        return Response({"error": "쿼리 파라미터 형식을 지켜주세요. YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)
    
    today = date.today()
    if selected_date != today:
        return Response({"error": "오늘의 기록만 삭제 할 수 있어요!"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        chat = Chat.objects.get(id=id)
    except chat.DoesNotExist:
        return Response({"error": "삭제할 메세지가 없습니다."}, status=status.HTTP_404_NOT_FOUND)
    
    chat.delete()
    return Response({"삭제된 메세지입니다."}, status=status.HTTP_200_OK)   # 메세지 삭제 성공