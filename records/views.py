from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from records.models import Record
from records.serializers import RecordSerializer
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from django.utils.timezone import make_aware

from django.views.decorators.csrf import csrf_exempt
from krwordrank.word import summarize_with_keywords
import os
from wordcloud import WordCloud
from reportlab.lib.pagesizes import letter
from django.conf import settings


"""
    < archive >
"""
# archive : 긴 글 모아보기
@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])   # 로그인 유저만 권한 있음
def archive(request):
    # 쿼리 파라미터로 필터링 옵션 받기
    filter_liked    = request.GET.get('liked', None)
    order_by_date   = request.GET.get('order_by', None)
    category        = request.GET.get('category', None)
    keyword         = request.GET.get('keyword', None)

    # 레코드 쿼리셋 필터링 및 정렬
    records = Record.objects.filter(writer = request.user)
    if category == '북마크':
        records = records.filter(liked=True)
    elif category:
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

# archive 중 글 한 개 조회
@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])   # 로그인 유저만 권한 있음
def detail_archive(request, id):
    try:
        record = Record.objects.get(id=id)
    except Record.DoesNotExist:
        return Response({"error": "기록을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

    record_serializer = RecordSerializer(record)
    return Response(record_serializer.data, status=status.HTTP_200_OK)





"""
      < 주의 >
      긴글모드에서 진행!!! 모아보기랑 관련 없음!!!
"""
# 긴글 수정 및 삭제
@csrf_exempt
@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])   # 로그인 유저만 권한 있음
def modify_record(request, id):
    date_query_param = request.GET.get('date', None)
    mode = request.GET.get('mode', None)
    if not date_query_param:
        return Response({"error": "쿼리 파라미터가 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
    if mode != 'record':
        return Response({"error": "긴글 모드를 이용해주세요!"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        record = Record.objects.get(id=id)
    except Record.DoesNotExist:
        return Response({"error": "작성한 글이 없습니다!"}, status=status.HTTP_404_NOT_FOUND)
    
    match request.method:
        case 'PATCH':   
            data = request.data
            if not any(field in data for field in ['title', 'content', 'liked']):
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

        case 'DELETE':
            record.delete()
            return Response({"message": "삭제 성공!"}, status=status.HTTP_200_OK)
        

"""
    < WordCloud >
"""
# 워드 클라우드 생성 함수 : texts 받고 image 반환
def generate_wordcloud(texts):
    # const
    font_path = os.path.join(settings.BASE_DIR, 'DungGeunMo.woff')
    stopwords = { # 불용어
        '너무', '정말', '아주', '매우', '굉장히', '상당히', '무척', '엄청', '몹시', '너무나', '대단히', '정말로', '실로', '진짜', '참으로', 
        '물론', '다소', '약간', '조금', '많이', '그야말로', '대단히', '일부', '더욱', '특히',
        '을', '를', '에', '의', '이', '가', '은', '는', '도', '로', '와', '과', '제', '한', '그', '저', '이', '각', '것', '수', '듯', '바',
        '그리고', '그러고', '그러나', '그래서', '그러면', '그러나', '그렇지만',
        '것을', '것이', '있는', '싶다', '나니', '때문', '이런', '저런', '그런', '어떤', '모든', '아무', '통해', '다시', '마치',
        '어제', '내일', '모레', '지금', '그때', '언제', '항상', '자주', '가끔', '때때로', '이번', '다음',
        '이렇게', '것을', '같다.', '되었다.', '남았다.', '.', '같은', '있었', '했어.', 
        # '오늘', 
        } 
    
    # NLP
    keywords = summarize_with_keywords(
        texts, min_count=1, max_length=10, 
        beta=0.85, max_iter=10, stopwords=stopwords, verbose=True )

    # 워드 클라우드 생성
    frequencies = {key: val for key, val in keywords.items()}
    wordcloud = WordCloud(
        width=800, height=400, 
        background_color='white', 
        stopwords=stopwords,
        font_path=font_path
    ).generate_from_frequencies(frequencies)

    return wordcloud.to_image()

# 워드 클라우드 최초 생성
def make_wordcloud(request):
    ver = request.GET.get('wordcloud', 'week')
    now = datetime.now()
    # month / week 에 따라 data 담기
    if ver == 'month':
        current_month_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        start = current_month_start - timedelta(seconds=1) # 지난 달 마지막 날
        end = start.replace(day=1, hour=0, minute=0, second=0, microsecond=0) #지난 달 첫 날
        # 이미지 파일 이름 지정
        image_name = now.strftime("%Y%m") + "_month.png" 
    else: # week
        current_start = now.replace(hour=0, minute=0, second=0, microsecond=0)   # 월요일 00시00분00초
        start = current_start - timedelta(days=7) # 지난 주 월요일
        end = current_start - timedelta(seconds=1) # 지난 주 일요일
        # 이미지 파일 이름 지정
        image_name = now.strftime("%Y%m%d") + "_week.png"
    
    # 시간대를 인식하는 datetime 객체로 변환 (Django에서 사용하는 timezone aware datetime 객체)
    range_start = make_aware(start)
    range_end = make_aware(end)

    records = Record.objects.filter(writer=request.user, created_at__range=[range_start, range_end])
    texts = [record.content for record in records]
    if not texts: # 프론트에서 "지난 ~ 간 글이 없어요!" 등 띄우기
        return Response({"message": "No text content found in records"}, status=404)
    
    # 워드클라우드 이미지 생성
    wordcloud_image = generate_wordcloud(texts)
    
    # 이미지 파일로 변환
    image_path = os.path.join(settings.MEDIA_ROOT, image_name)
    wordcloud_image.save(image_path)

    if not os.path.exists(image_path):
        print("Image file was not saved.")
        return Response({"message": "Failed to save image file"}, status=500)

    image_url = settings.MEDIA_URL + image_name
    return Response({"image_url": image_url})

# 워드 클라우드 조회 함수
@api_view(['GET'])
def get_wordcloud(request):
    date_query_param = request.GET.get('date', None)
    date_obj = datetime.strptime(date_query_param, '%Y-%m-%d')
    ver = request.GET.get('wordcloud', 'week')
    now = datetime.now()

    if ver == 'month': # 지난 달 파일을 주기
        yearmonth = date_obj.strftime('%Y%m')
        image_name = yearmonth + "_month.png"
        
    else: # 해당 주 월요일 날짜 파일을 주기
        weekday = date_obj.weekday()  
        start_of_week = date_obj - timedelta(days=date_obj.weekday())
        yearmonthdate = start_of_week.strftime('%Y%m%d')
        image_name = yearmonthdate + "_week.png"

    image_url = settings.MEDIA_URL + image_name
    return Response({"image_url": image_url})