from django.contrib.auth.models import AbstractUser
from django.db import models

USER_ROLE = (
    (1, 'Student'),
    (2, 'Teacher'),
)


class User(AbstractUser):
    role = models.PositiveIntegerField(choices=USER_ROLE, default=1)

    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)

    def __str__(self):
        return f'{self.last_name} {self.first_name}'
