from rest_framework import serializers

from authentication.serializers import UserSerializer
from exam.models import Test, Question, Option, Result, Answer


class AllTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = ('id', 'user', 'name', 'limit', 'time', 'total_questions', 'start_time', 'end_time')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user'] = UserSerializer(instance.user).data
        return data


class SingleTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = ('id', 'user', 'name', 'limit', 'time', 'total_questions', 'start_time', 'end_time')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user'] = UserSerializer(instance.user).data
        data['questions'] = QuestionSerializer(Question.objects.filter(test_id=instance.id), many=True).data
        return data


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('id', 'test', 'text')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['Options'] = OptionSerializer(Option.objects.filter(question_id=instance.id), many=True).data
        return data

    def create(self, validated_data):
        test_id = validated_data['test'].id
        question = Question.objects.create(**validated_data)

        test = Test.objects.filter(id=test_id).first()
        test.total_questions += 1
        test.save()

        return question


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ('id', 'question', 'text', 'is_correct')


class TakeOptionSerializer(serializers.Serializer):
    question = serializers.IntegerField()
    answer = serializers.IntegerField()


class TakeTestSerializer(serializers.Serializer):
    test = serializers.IntegerField()
    answers = serializers.ListField(child=TakeOptionSerializer())


class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = ('id', 'user', 'test', 'total_questions', 'correct_answers')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user'] = UserSerializer(instance.user).data
        data['test'] = SingleTestSerializer(instance.test).data
        data['answers'] = AnswerSerializer(Answer.objects.filter(result_id=instance.id), many=True).data
        return data


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ('id', 'question', 'student_answer', 'correct_answer')
