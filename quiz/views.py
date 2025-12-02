from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from .models import DailyQuiz,QuizAnswerOption,QuizAnswer
from .serializers import (
    DailyQuizSerializer,
    QuizAnswerOptionSerializer,
    QuizAnswerSubmitSerializer,
    QuizAnswerOptionReadSerializer

)


class DailyQuizListCreate(APIView):

    def get(self,request):
        quizzes = DailyQuiz.objects.all()
        serializer = DailyQuizSerializer(quizzes,many = True)
        return Response(serializer.data)
    

    def post(self,request):
        serializer = DailyQuizSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"Quiz created successfully "},status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DailyQuizDetail(APIView):

    def get(self,request,pk):
        quiz = get_object_or_404(DailyQuiz,pk=pk)
        serializer = DailyQuizSerializer(quiz)
        return Response(serializer.data)
    
    def put(self,request,pk):
        quiz = get_object_or_404(DailyQuiz,pk=pk)
        serializer = DailyQuizSerializer(quiz,data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"Quiz updated"})
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    def delete(self,request,pk):
        quiz = get_object_or_404(DailyQuiz,pk=pk)
        quiz.delete()
        return Response({"message":"Quiz deleted"})
    

# Quiz_list


class QuizOptionListCreate(APIView):
    def get(self,request):
        options = QuizAnswerOption.objects.all()
        serializer = QuizAnswerOptionReadSerializer(options, many =True)
        return Response(serializer.data)
    def post(self,request):
        serializer = QuizAnswerOptionSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"option created successfully"},status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    


class QuizOptionDetail(APIView):
    def get(self,request,pk):
        option = get_object_or_404(QuizAnswerOption,pk=pk) 
        serializer = QuizAnswerOptionSerializer(option)
        return Response(serializer.data)
    def put(self,request,pk):
        option =get_object_or_404(QuizAnswerOption,data = request.data)
        serializer = QuizAnswerOptionSerializer(option,data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"Option updated  successfully"})
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    def delete(self,request,pk):
        option = get_object_or_404(QuizAnswerOption,pk=pk)
        option.delete()
        return Response({"message":"Option deleted successfully"})
    
       


class SubmitQuizAnswer(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = QuizAnswerSubmitSerializer(data=request.data,context={"request": request} )
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response(result)

