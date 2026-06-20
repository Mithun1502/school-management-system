from django.contrib import admin
from .models import Teacher, Standard, Student



# Register your models here.

admin.site.register(Standard)
admin.site.register(Teacher)
admin.site.register(Student)
