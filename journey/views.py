from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Journey,JourneyDetails,Journey_icon,Days
from .serializers import JourneySerilzers,JourneyDetailsSerializer,Journey_icon,DaysSerializer,JourneyIconSerializer

from .utils import get_today_journey_id

from datetime import date
# current journey

class JourneyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        user = request.user
        
        result = get_today_journey_id(user)

        if result is None:
            return Response({"error":"No journey available for this user"},status=status.HTTP_400_BAD_REQUEST)
        
        journdy_id , day_number = result

        journey = Journey.objects.filter(id=journdy_id).first()
        serializer = JourneySerilzers(journey)

        return Response({
            "data":str(date.today()),
            "day_number":day_number,
            "journey_id":journdy_id,
            "journey":serializer.data
        })




# JOURNEY VIEW


class JourneyListCreateAPIView(APIView):
    def get(self, request):
        journeys = Journey.objects.all()
        serializer = JourneySerilzers(journeys, many=True, context={"request": request})
        return Response(serializer.data)

    def post(self, request):
        serializer = JourneySerilzers(data=request.data)

        # Check duplicate by name
        journey_name = request.data.get("name")

        if Journey.objects.filter(name=journey_name).exists():
            return Response({"message": "Journey already exists"}, status=400)

        # Validate and save
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Journey created successfully",
            }, status=201)

        return Response(serializer.errors, status=400)




class SingleJourneyAPIview(APIView):
    def get_obj(self,pk):
        try:
            return Journey.objects.get(pk=pk)
        except Journey.DoesNotExist:
            return None

    def get(self,request,pk):
        journey = self.get_obj(pk)
        if journey is None:
            return Response({"error":"Jouney not found"},status=status.HTTP_404_NOT_FOUND)

        serializer = JourneySerilzers(journey)
        return Response(serializer.data)
    
    def put(self,request,pk):
        jouney = self.get_obj(pk)
        if jouney is None:
            return Response({"error":"Journey not found"},status=status.HTTP_400_BAD_REQUEST)
        
        serializer = JourneySerilzers(jouney, data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    

    def delete(self,request,pk):
        jouney = self.get_obj(pk)
        if jouney is None:
            return Response({"error":"Journey not found"},status=status.HTTP_400_BAD_REQUEST)
        jouney.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


#   JOURNEY DETAILS VIEW    


class JourneyDetailsListCreateAPIView(APIView):
    def get(self,request):
        data = JourneyDetails.objects.all()
        serializer = JourneyDetailsSerializer(data, many =True)
        return Response(serializer.data)
    
    def post(self,request):
        serializer = JourneyDetailsSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                "message": "Journey Details created successfully",
                },status =status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    

class JourneyDetailsAPIView(APIView):
    def get_obj(self,pk):
        try:
            return JourneyDetails.objects.get(pk=pk)
        except JourneyDetails.DoesNotExist:
            return None

    def get(self,request,pk):
        obj = self.get_obj(pk)
        if obj is None:
            return Response({"error":"Details not found "}, status=status.HTTP_400_BAD_REQUEST)
        serializer = JourneyDetailsSerializer(obj)
        return Response(serializer.data)
    
    def put(self,request,pk):
        obj = self.get_obj(pk)
        if obj is None:
            return Response({"error":"Details not found"},status=status.HTTP_400_BAD_REQUEST)
        serializer = JourneyDetailsSerializer(obj, data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request,pk):
        obj = self.get_obj()
        if obj is None:
            return Response({"error":"Details not found"},status=status.HTTP_400_BAD_REQUEST)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

# Days views

class DayListCreateAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        days = Days.objects.all()
        serializer = DaysSerializer(days, many=True, context={"request": request})
        return Response(serializer.data)

    def post(self, request):
        serializer = DaysSerializer(data=request.data, context={"request": request})
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Journey days created"},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class DaysAPIView(APIView):
    def get_obj(self,pk):
        try:
            return Days.objects.get(pk=pk)
        except Days.DoesNotExist:
            return None

    def get(self,request,pk):
        obj = self.get_obj(pk)
        if obj is None:
            return Response({"error": "Days not found"},status = status.HTTP_400_BAD_REQUEST)
        serializer = DaysSerializer(obj)
        return Response(serializer.data)
    
    def put(self,request,pk):
        obj = self.get_obj(pk)
        if obj is None:
            return Response({"errors":"Days not found"},status=status.HTTP_400_BAD_REQUEST)
        serializer = DaysSerializer(obj, data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request,pk):
        obj = self.get_obj(pk)
        if obj is None:
            return Response({"error":"Daya not found"}, status=status.HTTP_400_BAD_REQUEST)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    

        
# Journey_icon Views



class JourneyIconListView(APIView):
    def get(self,request):
        data = Journey_icon.objects.all()
        serializer = JourneyIconSerializer(data, many=True, context={"request": request})
        return Response(serializer.data)
    def post(self,request):
        serializer = JourneyIconSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"Icon add succsfull"},status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=400)
    

class JourneyIconAPiView(APIView):
    def get_obj(self,pk):
        try:
            return Journey_icon.objects.get(pk=pk)
        except Journey_icon.DoesNotExist:
            return None
        
    def get(self,request,pk):
        obj = self.get_obj(pk)
        if obj is None:
            return Response({"error":"Icon not found"},status=status.HTTP_400_BAD_REQUEST)
        serializer = JourneyIconSerializer(obj)
        request (serializer.data)    

    def put(self,request,pk):
        obj = self.get_obj(pk)
        if obj is None:
            return Response({"error":"Icon not found"},status=status.HTTP_400_BAD_REQUEST)
        serializer = JourneyIconSerializer(obj, data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def delete(self,request,pk):
        obj = self.get_obj(pk)
        if obj is None:
            return Response({"error":"Icon not found"},status=status.HTTP_400_BAD_REQUEST)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)    


    




