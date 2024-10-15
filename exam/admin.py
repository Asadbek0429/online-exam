from django.contrib import admin
from .models import Test, Question, Answer, Result, Option


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'time', 'limit')
    list_display_links = ('id', 'user')
    search_fields = ('user__first_name', 'user__last_name', 'name')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'test', 'text')
    list_display_links = ('id', 'test')
    search_fields = ('text', 'test__name', 'test__id')


@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'text', 'is_correct')
    list_display_links = ('id', 'question')
    search_fields = ('question__id', 'question__text', 'text')


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'test', 'total_questions', 'correct_answers')
    list_display_links = ('id', 'user', 'test')
    search_fields = ('user__first_name', 'user__last_name', 'user__id', 'test__id', 'test__name')


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'question', 'student_answer', 'correct_answer')
    list_display_links = ('id', 'question')
    search_fields = ('question__id', 'question__text', 'text')
