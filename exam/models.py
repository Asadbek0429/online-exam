from django.db import models

from abstraction.base_model import BaseModel
from authentication.models import User


class Test(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    limit = models.PositiveIntegerField(default=0)
    time = models.DurationField()
    total_questions = models.PositiveIntegerField(default=0)

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return self.name


class Question(BaseModel):
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    text = models.TextField()

    def __str__(self):
        return self.text


class Option(BaseModel):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.TextField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class Result(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    total_questions = models.PositiveIntegerField(default=0)
    correct_answers = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.user.first_name


class Answer(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    student_answer = models.ForeignKey(Option, on_delete=models.CASCADE, related_name="student_answer")
    correct_answer = models.ForeignKey(Option, on_delete=models.CASCADE, related_name="correct_answer")
    result = models.ForeignKey(Result, on_delete=models.CASCADE)
