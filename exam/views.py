from datetime import datetime

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from .models import Test, Question, Option, Result, Answer
from .serializers import (
    AllTestSerializer, SingleTestSerializer, QuestionSerializer, OptionSerializer, TakeTestSerializer, ResultSerializer)


class TestViewSet(ViewSet):
    @swagger_auto_schema(
        responses={200: AllTestSerializer()},
        operation_summary="Get All Available Tests",
        operation_description="Get all available test",
        tags=['Test'],
    )
    def get_tests(self, request, *args, **kwargs):
        tests = Test.objects.filter(end_time__gt=datetime.now())
        serializer = AllTestSerializer(tests, many=True)
        return Response(data={'result': serializer.data}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        responses={200: SingleTestSerializer()},
        operation_summary="Get Test",
        operation_description="Get test",
        tags=['Test'],
    )
    def get_test(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        test = Test.objects.filter(id=pk).first()
        if not test:
            return Response(data={'result': '', 'error': 'Exam Not Found'}, status=status.HTTP_404_NOT_FOUND)
        if test.end_time <= datetime.now() and test.user.id != request.user.id:
            return Response(data={'result': '', 'error': 'Exam is over'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = SingleTestSerializer(test)
        return Response(data={'result': serializer.data}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Test Name'),
                'time': openapi.Schema(type=openapi.TYPE_STRING, description='Duration'),
                'start_time': openapi.Schema(type=openapi.TYPE_STRING, description='Start Time'),
                'end_time': openapi.Schema(type=openapi.TYPE_STRING, description='End Time'),
            }
        ),
        responses={201: SingleTestSerializer()},
        operation_summary="Create Test",
        operation_description="Create test",
        tags=['Test'],
    )
    def create_test(self, request, *args, **kwargs):
        data = request.data
        data['user'] = request.user.id
        serializer = SingleTestSerializer(data=data)
        if not serializer.is_valid():
            return Response(data={'result': '', 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(data={'result': serializer.data}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Test Name'),
                'time': openapi.Schema(type=openapi.TYPE_STRING, description='Duration'),
                'start_time': openapi.Schema(type=openapi.TYPE_STRING, description='Start Time'),
                'end_time': openapi.Schema(type=openapi.TYPE_STRING, description='End Time'),
            }
        ),
        responses={200: SingleTestSerializer()},
        operation_summary="Update Test",
        operation_description="Update test",
        tags=['Test'],
    )
    def update_test(self, request, *args, **kwargs):
        data = request.data
        data['user'] = request.user.id
        test = Test.objects.filter(id=kwargs.get('pk')).first()
        if test.user.id != request.user.id:
            return Response(data={'result': '', 'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        serializer = SingleTestSerializer(test, data, partial=True)
        if not serializer.is_valid():
            return Response(data={'result': '', 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(data={'result': serializer.data}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        responses={204: 'Successfully deleted'},
        operation_summary="Delete Test",
        operation_description="Delete test",
        tags=['Test'],
    )
    def delete_test(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        test = Test.objects.filter(id=pk).first()
        if test.user.id != request.user.id:
            return Response(data={'result': '', 'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        if not test:
            return Response(data={'result': '', 'error': 'Exam Not Found'}, status=status.HTTP_404_NOT_FOUND)
        test.delete()
        return Response(data={'result': 'Successfully deleted'}, status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        responses={200: ResultSerializer()},
        operation_summary="Start Test",
        operation_description="Start test",
        tags=['Test'],
    )
    def start_test(self, request, *args, **kwargs):
        test = Test.objects.filter(id=kwargs.get('pk'), start_time__lt=datetime.now(),
                                   end_time__gt=datetime.now()).first()
        if not test:
            return Response(data={'result': '', 'error': 'Test Not Found'}, status=status.HTTP_400_BAD_REQUEST)

        result = Result.objects.filter(test_id=test.id)
        if result.count() >= test.limit:
            return Response(data={'result': '', 'error': 'The limit has been exceeded'},
                            status=status.HTTP_400_BAD_REQUEST)
        if result.filter(user_id=request.user.id).exists():
            return Response(data={'result': '', 'error': 'You already took the exam'},
                            status=status.HTTP_400_BAD_REQUEST)

        obj = Result.objects.create(user_id=request.user.id, test=test, total_questions=test.total_questions)
        obj.save()

        return Response(data={'result': ResultSerializer(obj).data}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        request_body=TakeTestSerializer(),
        responses={200: TakeTestSerializer()},
        operation_summary="Take Test",
        operation_description="Take test",
        tags=['Test'],
    )
    def take_test(self, request, *args, **kwargs):
        data = request.data
        data['user'] = request.user.id
        serializer = TakeTestSerializer(data=data)
        if not serializer.is_valid():
            return Response(data={'result': '', 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        test = Test.objects.filter(id=data['test']).first()
        if not test:
            return Response(data={'result': '', 'error': 'Test Not Found'}, status=status.HTTP_400_BAD_REQUEST)

        result = Result.objects.filter(test_id=test.id, user_id=request.user.id).first()
        if not result:
            return Response(data={'result': '', 'error': "You haven't begun the exam yet!"},
                            status=status.HTTP_400_BAD_REQUEST)

        answers = Answer.objects.filter(result_id=result.id, user_id=request.user.id).exists()
        if answers:
            return Response(data={'result': '', 'error': "You have already completed this exam"},
                            status=status.HTTP_400_BAD_REQUEST)

        correct_answers = 0
        for answer in serializer.validated_data['answers']:
            correct_answer = Option.objects.filter(question_id=answer['question'], question__test_id=test.id,
                                                   is_correct=True).first()
            answer_ = Answer.objects.create(user_id=request.user.id, question_id=answer['question'],
                                            student_answer_id=answer['answer'], correct_answer_id=correct_answer.id,
                                            result_id=result.id)
            answer_.save()
            if correct_answer and correct_answer.id == answer['answer']:
                correct_answers += 1

        result.correct_answers = correct_answers
        result.save()

        return Response(data={'result': ResultSerializer(result).data}, status=status.HTTP_201_CREATED)


class QuestionViewSet(ViewSet):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(name='test', type=openapi.TYPE_INTEGER, in_=openapi.IN_QUERY, required=True)
        ],
        responses={200: QuestionSerializer()},
        operation_summary="Get Questions By Test Id",
        operation_description="Get questions by test id",
        tags=['Question'],
    )
    def get_questions(self, request, *args, **kwargs):
        data = request.GET
        questions = Question.objects.filter(test_id=data.get('test'))
        serializer = QuestionSerializer(questions, many=True)
        return Response(data={'result': serializer.data}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        responses={200: QuestionSerializer()},
        operation_summary="Get Question By Id",
        operation_description="Get question by id",
        tags=['Question'],
    )
    def get_question(self, request, *args, **kwargs):
        question = Question.objects.filter(id=kwargs.get('pk')).first()
        if not question:
            return Response(data={'result': '', 'error': 'Question Not Found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = QuestionSerializer(question)
        return Response(data={'result': serializer.data})

    @swagger_auto_schema(
        request_body=QuestionSerializer(),
        responses={201: QuestionSerializer()},
        operation_summary="Create Question",
        operation_description="Create question",
        tags=['Question'],
    )
    def create_question(self, request, *args, **kwargs):
        data = request.data
        serializer = QuestionSerializer(data=data)
        if not serializer.is_valid():
            return Response(data={'result': '', 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        if serializer.validated_data['test'].user.id != request.user.id:
            return Response(data={'result': '', 'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        serializer.save()
        return Response(data={'result': serializer.data}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        request_body=QuestionSerializer(),
        responses={200: QuestionSerializer()},
        operation_summary="Update Question",
        operation_description="Update question",
        tags=['Question'],
    )
    def update_question(self, request, *args, **kwargs):
        data = request.data
        question = Question.objects.filter(id=kwargs.get('pk')).first()
        if not question:
            return Response(data={'result': '', 'error': 'Question Not Found'}, status=status.HTTP_404_NOT_FOUND)

        data['test'] = question.test.id
        serializer = QuestionSerializer(question, data, partial=True)
        if not serializer.is_valid():
            return Response(data={'result': '', 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        if question.test.user.id != request.user.id:
            return Response(data={'result': '', 'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        serializer.save()
        return Response(data={'result': serializer.data}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        request_body=QuestionSerializer(),
        responses={204: "Successfully deleted"},
        operation_summary="Delete Question",
        operation_description="Delete question",
        tags=['Question'],
    )
    def delete_question(self, request, *args, **kwargs):
        question = Question.objects.filter(id=kwargs.get('pk')).first()

        if not question:
            return Response(data={'result': '', 'error': 'Question Not Found'}, status=status.HTTP_404_NOT_FOUND)
        if question.test.user.id != request.user.id:
            return Response(data={'result': '', 'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        question.delete()
        return Response(data={'result': 'Successfully deleted'}, status=status.HTTP_204_NO_CONTENT)


class OptionViewSet(ViewSet):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(name='question', type=openapi.TYPE_INTEGER, in_=openapi.IN_QUERY, required=True)
        ],
        responses={200: OptionSerializer()},
        operation_summary="Get Options By Question Id",
        operation_description="Get Options by Question id",
        tags=['Option'],
    )
    def get_options(self, request, *args, **kwargs):
        data = request.GET
        options = Option.objects.filter(question_id=data.get('question'))
        serializer = OptionSerializer(options, many=True)
        return Response(data={'result': serializer.data}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        responses={200: OptionSerializer()},
        operation_summary="Get Option By Id",
        operation_description="Get Option by id",
        tags=['Option'],
    )
    def get_option(self, request, *args, **kwargs):
        option = Option.objects.filter(id=kwargs.get('pk')).first()
        if not option:
            return Response(data={'result': '', 'error': 'Option Not Found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = OptionSerializer(Option)
        return Response(data={'result': serializer.data})

    @swagger_auto_schema(
        request_body=OptionSerializer(),
        responses={201: OptionSerializer()},
        operation_summary="Create Option",
        operation_description="Create Option",
        tags=['Option'],
    )
    def create_option(self, request, *args, **kwargs):
        data = request.data
        serializer = OptionSerializer(data=data)
        if not serializer.is_valid():
            return Response(data={'result': '', 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        if serializer.validated_data['question'].test.user.id != request.user.id:
            return Response(data={'result': '', 'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        serializer.save()
        return Response(data={'result': serializer.data}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        request_body=OptionSerializer(),
        responses={200: OptionSerializer()},
        operation_summary="Update Option",
        operation_description="Update Option",
        tags=['Option'],
    )
    def update_option(self, request, *args, **kwargs):
        data = request.data
        option = Option.objects.filter(id=kwargs.get('pk')).first()
        if not option:
            return Response(data={'result': '', 'error': 'Option Not Found'}, status=status.HTTP_404_NOT_FOUND)

        data['question'] = option.question.id
        serializer = OptionSerializer(Option, data, partial=True)
        if not serializer.is_valid():
            return Response(data={'result': '', 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        if option.question.test.user.id != request.user.id:
            return Response(data={'result': '', 'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        serializer.save()
        return Response(data={'result': serializer.data}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        request_body=OptionSerializer(),
        responses={204: "Successfully deleted"},
        operation_summary="Delete Option",
        operation_description="Delete Option",
        tags=['Option'],
    )
    def delete_option(self, request, *args, **kwargs):
        option = Option.objects.filter(id=kwargs.get('pk')).first()

        if not option:
            return Response(data={'result': '', 'error': 'Option Not Found'}, status=status.HTTP_404_NOT_FOUND)
        if option.question.test.user.id != request.user.id:
            return Response(data={'result': '', 'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        option.delete()
        return Response(data={'result': 'Successfully deleted'}, status=status.HTTP_204_NO_CONTENT)


class TestStatsViewSet(ViewSet):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(name='test', type=openapi.TYPE_INTEGER, in_=openapi.IN_QUERY, required=True)
        ],
        responses={200: ResultSerializer()},
        operation_summary="Get User Statistic By Test Id",
        operation_description="Get user statistic by test id",
        tags=['Test'],
    )
    def get_by_user(self, request, *args, **kwargs):
        result = Result.objects.filter(user_id=request.user.id, test_id=request.GET.get('test')).first()
        serializer = ResultSerializer(result)
        return Response(data={'result': serializer.data}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        responses={200: ResultSerializer()},
        operation_summary="Get Test Statistic",
        operation_description="Get test statistic",
        tags=['Test'],
    )
    def get_by_test(self, request, *args, **kwargs):
        results = Result.objects.filter(test_id=kwargs.get('pk'))
        serializer = ResultSerializer(results, many=True)
        return Response(data={'result': serializer.data}, status=status.HTTP_200_OK)
