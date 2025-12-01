from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import DailyDevotion,DailyPrayer,MicroAction
from  .serializers import(
    DailyDevotionSerializer,
    DailyPrayerSerializer,
    MicroActionSerializer,
    ReflectionSpaceSerializer,
)


# ---------------- Daily Devotion Views ---------------- #

class DailyDevotionListCreate(APIView):
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
    


class ReflectionSpaceAPIView(APIView):
 

    def post(self, request):
        serializer = ReflectionSpaceSerializer(data=request.data)

        if serializer.is_valid():
            note = serializer.validated_data.get("note")

            # Always save with user
            reflection = serializer.save(user_id=request.user)

            if not note:
                return Response({"message": "Reflection is empty."})

            return Response({"message": "Reflection Saved"})

        return Response(serializer.errors, status=400)
  

        

        
# ---------------- Daily Prayer Views ---------------- #

class DailyPrayerListCreate(APIView):
    def get(self,request):
        data = DailyPrayer.objects.all()
        serializer = DailyPrayerSerializer(data,many = True,context={"request": request})
        return Response(serializer.data)
    def post(self,request):
        serializer = DailyPrayerSerializer(data = request.data,context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Daily Prayer created successfully"},status=status.HTTP_201_CREATED)
        return  Response(serializer.errors,status = status.HTTP_400_BAD_REQUEST)

class DailyPrayerDetail(APIView):
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
    def get(self,request):
        data = MicroAction.objects.all()    
        serializer = MicroActionSerializer(data, many = True)
        return Response(serializer.data)
    
    def post(self,request):
        serializer = MicroActionSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"Micro Action created successfully"},status=status.HTTP_201_CREATED)



class MicroActionDetail(APIView):
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
        
        
        

