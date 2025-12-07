from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated ,AllowAny
from .models import DailyDevotion,DailyPrayer,MicroAction
from  .serializers import(
    DailyDevotionSerializer,
    DailyPrayerSerializer,
    MicroActionSerializer,  
    DailyReflicationSerializer,
)


# ---------------- Daily Devotion Views ---------------- #

class DailyDevotionListCreate(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        data = DailyDevotion.objects.all()
        serializer = DailyDevotionSerializer(data,many=True)
        return Response(serializer.data)
    
    def post(self,request):
        serializer = DailyDevotionSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Daily Devotion created successfully"},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    

class DailDevotionDetails(APIView):
    permission_classes = [IsAuthenticated]
    def get_obj(self,pk):
        try:
            return DailyDevotion.objects.get(pk = pk)
        except DailyDevotion.DoesNotExist:
            return None
    def get(self,request,pk):
        item = self.get_obj(pk)
        if item is None:
            return Response({"error":"DailyDevotion not found"},status=status.HTTP_404_NOT_FOUND)
        
        serializer = DailyDevotionSerializer(item)
        return Response(serializer.data)
    
    def put(self,request,pk):
        item = self.get_obj(pk)
        if item is None:
            return Response({"error":"DailyDevotion not found"},status=status.HTTP_404_NOT_FOUND)
        serializer = DailyDevotionSerializer(item,data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"Updated successfully"})
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    def delete(self,request,pk):
        item = self.get_obj(pk)
        if item is None:
            return Response({"error":"DailyDevotion not found"},status= status.HTTP_400_BAD_REQUEST)
        item.delete()
        return Response({"message":"Deleted successfully"})
    
#----------ReflectionSPace


class DailyReflectionSpace(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        serializer = DailyReflicationSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save(user = request.user)
            return Response(
                {"message":"Reflection saved"},
                    status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        

        
# ---------------- Daily Prayer Views ---------------- #
import requests
from django.core.files.base import ContentFile
class DailyPrayerListCreate(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        data = DailyPrayer.objects.all()
        serializers = DailyPrayerSerializer(data, context={"request": request},many = True)
        return Response(serializers.data)
    def post(self, request):
        # 1 validate
        serializer = DailyPrayerSerializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # 2 save prayer first
        obj = serializer.save()  # now obj has id, prayer, journey, day

        # 3build external request payload
        payload = {
            "text": obj.prayer,
            "voice": "alloy",
            "model": "tts-1",
            "speed": 1,
            "save_file": False,
            "filename": f"prayer_{obj.id}.mp3"
        }

        # 4 hit external audio stream API
        try:
            res = requests.post(
                "http://206.162.244.135:8001/api/stream",
                json=payload
            )
        except Exception as e:
            return Response({"error": f"Audio API failed: {str(e)}"}, status=500)

        #  save binary audio to Django
        if res.status_code == 200:
            obj.audio.save(
                f"prayer_{obj.id}.mp3",
                ContentFile(res.content),
                save=True
            )

        # 6 build final response
        audio_url = None
        if obj.audio:
            audio_url = request.build_absolute_uri(obj.audio.url)

        return Response({
            "id": obj.id,
            "prayer": obj.prayer,
            "audio_url": audio_url
        }, status=201)



class DailyPrayerDetail(APIView):
    permission_classes = [IsAuthenticated]
    def get_obj(self,pk):
        try:
            return DailyPrayer.objects.get(pk=pk)
        except DailyPrayer.DoesNotExist:
            return None
    def get(self,request,pk):
        item = self.get_obj(pk)
        if item is None:
            return Response({"error":" Not found "},status=status.HTTP_404_NOT_FOUND)
        serializer = DailyPrayerSerializer(item,context={"request": request})
        return Response(serializer.data)
    def put(self,request,pk):
        item = self.get_obj(pk)
        if item is None:
            return Response({"error":"Not found"},status=status.HTTP_404_NOT_FOUND)
        serializer = DailyPrayerSerializer(item ,data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"Updated successfully"})
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    def delete(self,request,pk):
        item = self.get_obj(pk)
        if item is None:
            return Response({"error":"Not found"},status=status.HTTP_404_NOT_FOUND)
        item.delete()
        return Response({"message":"Deleted Successfully"})
    
# ---------------- Micro Action Views ---------------- #

class MicroActionListCreate(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        data = MicroAction.objects.all()    
        serializer = MicroActionSerializer(data, many = True)
        return Response(serializer.data)
    
    def post(self,request):
        serializer = MicroActionSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"Micro Action created successfully"},status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class MicroActionDetail(APIView):
    permission_classes = [IsAuthenticated]
    def get_obj(self,pk):
        try:
            return MicroAction.objects.get(pk=pk)
        except MicroAction.DoesNotExist:
            return None
    def get(self,request,pk):
        item = self.get_obj(pk)
        if item is None:
            return Response({"error":"Not found"},status=status.HTTP_404_NOT_FOUND)
        serializer = MicroActionSerializer(item)
        return Response(serializer.data)    
    def put(self,request,pk):
        item = self.get_obj(pk)
        if item is None:
            return Response({"error":"Not forund"},status=status.HTTP_404_NOT_FOUND)
        serializer = MicroActionSerializer(item, data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"Updated successfully"})
        return Response(serializer.errors,status = status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request,pk):
        item = self.get_obj(pk)
        if item is None:
            return Response({"error":"Not found"},status=status.HTTP_404_NOT_FOUND)
        item.delete()
        return Response({"message":"Deleted successfully"})
        
        
# ========================================
#       SEQUENCE BASED TODAY VIEWS
# ========================================


# from .utils import get_today_ids

# class TodayDevotionView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self,request):

#         journey_id , day_id , day_number = get_today_ids(request.user)
#         print("DEBUG:", journey_id, day_id, day_number)


#         if not journey_id or not day_id:
#             return Response({"error":"No content available"},status=status.HTTP_404_NOT_FOUND)
        
#         devetion = DailyDevotion.objects.filter(journey_id=journey_id,day_id=day_id).first()

#         data = DailyDevotionSerializer(devetion).data if devetion else {}

#         return Response({
#             "journey_id":journey_id,
#             "day_id":day_id,
#             "devetion":data
#         })




# class TodayPrayerView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self,request):
#         user = request.user

#         journey_id, day_id , day_number = get_today_ids(user)
        
#         prayer = DailyPrayer.objects.filter(journey_id=journey_id,day_id=day_id).first()
#         data = DailyPrayerSerializer(prayer).data if prayer else {}

#         return Response({
#             "journey_id":journey_id,
#             "day_id":day_id,
#             "prayer":data
#         })


# class TodayMicroActionView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self,request):
#         user = request.user
        
#         journey_id,day_id,day_number = get_today_ids(user)

#         action = MicroAction.objects.filter(journey_id=journey_id,day_id=day_id).first()
#         data = DailyDevotionSerializer(action).data if action else {}

#         return Response({
#             "journey_id":journey_id,
#             "day_id":day_id,
#             "prayer":data
#             })
