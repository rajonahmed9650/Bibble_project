from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from payments.permissions import HasActiveSubscription
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Journey,JourneyDetails,Journey_icon,Days
from .serializers import JourneySerilzers,JourneyDetailsSerializer,Journey_icon,DaysSerializer,JourneyIconSerializer
from payments.permissions import HasActiveSubscription


# JOURNEY VIEW


class JourneyListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated,HasActiveSubscription]
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
        serializer = JourneyDetailsSerializer(data, many =True,context={'request': request})
        return Response(serializer.data)
    
    def post(self,request):
        serializer = JourneyDetailsSerializer(data = request.data,context={'request': request})
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
        serializer = DaysSerializer(obj,context={'request': request})
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


    
from .models import PersonaJourney
from .serializers import JourneySerilzers,JourneyWithStatusSerializer
from payments.permissions import HasActiveSubscription
from .serializers import UserJourneyProgress


class UserJourneySequenceView(APIView):
    permission_classes = [IsAuthenticated, HasActiveSubscription]

    def get(self, request):
        user = request.user

        if not user.category:
            return Response(
                {"error": "User category not assigned"},
                status=400
            )

        persona = PersonaJourney.objects.get(persona=user.category)
        sequence = persona.sequence

        journeys = Journey.objects.filter(id__in=sequence)
        ordered = sorted(journeys, key=lambda j: sequence.index(j.id))

        serializer = JourneyWithStatusSerializer(
            ordered,
            many=True,
            context={"request": request}
        )

        # 🔑 find current journey (optional but useful)
        current = next(
            (j for j in serializer.data if j["status"] == "current"),
            None
        )

        return Response({
            "category": user.category,
            "current_journey": current,   # 👈 current journey clearly
            "journeys": serializer.data   # 👈 all journeys with status
        }, status=200)
