from django.db import models
from datetime import date


class Teacher(models.Model):
    name = models.CharField(max_length=100)
    standard = models.CharField(max_length=50)
    phone = models.CharField(max_length=10)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=255)

    address = models.TextField(default="")
    bank_account_number = models.CharField(max_length=18, default="")
    bank_branch = models.CharField(max_length=100, default="")
    ifsc_code = models.CharField(max_length=11, default="")

    def __str__(self):
        return self.name


class Standard(models.Model):
    standard_name = models.CharField(max_length=50)

    def __str__(self):
        return self.standard_name


class Student(models.Model):
    name = models.CharField(max_length=100)
    standard = models.CharField(max_length=20)
    roll_number = models.CharField(max_length=20, unique=True)
    phone = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50, unique=True, null=False)
    password = models.CharField(max_length=255, default="", null=False)

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="students",
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name


class Event(models.Model):
    title = models.CharField(max_length=100, default="School Event")
    description = models.TextField(default="No Description Available")
    event_image = models.ImageField(upload_to="events/", null=True, blank=True)
    event_date = models.DateField(default=date.today)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
