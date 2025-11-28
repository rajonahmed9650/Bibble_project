from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import DailyDevotion,DailyPrayer,MicroAction
from  .serializers import(
    DailyDevotionSerializer,
    DailyPrayerSerializer,
    MicroActionSerializer
)


# ---------------- Daily Devotion Views ---------------- #

class DailyDevotionListCreate(APIView):
    def get(self,request):
        data = DailyDevotion.objects.all()
        serializer = DailyPrayerSerializer(data,many=True)
        return Response(serializer.data)
    
    def post(self,request):
        serializer = DailyPrayerSerializer(data = request)
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
            return Response({"error":"DailyDevotion not found"},status=status.HTTP_400_BAD_REQUEST)
        
        serializer = DailyDevotionSerializer(item)
        return Response(serializer.data)
    
    def put(self,request,pk):
        item = self.get_obj(pk)
        if item is None:
            return Response({"error":"DailyDevotion not foune"},status=status.HTTP_400_BAD_REQUEST)
        serializer = DailyDevotionSerializer(item,data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"Updated successfully"})
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    def delete(self,request,pk):
        item = self.get_obj(pk)
        if item is None:
            return Response({"error":"DailyDevotion not found"},status= status.HTTP_404_NOT_FOUND)
        item.delete()
        return Response({"message":"Deleted successfully"})

        

        
