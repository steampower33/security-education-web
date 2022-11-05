from django.contrib import admin
from .models import ClassRoom, Classes

class ClassRoomAdmin(admin.ModelAdmin):
    search_fields = ['subject']

admin.site.register(ClassRoom, ClassRoomAdmin)
admin.site.register(Classes)