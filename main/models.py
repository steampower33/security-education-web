from django.db import models
from django.contrib.auth.models import User

class Classes(models.Model):
    educator = models.ForeignKey(User, on_delete=models.CASCADE)
    class_name = models.CharField(max_length=200)
    max_learner = models.IntegerField(default=0)
    learners = models.CharField(max_length=300, null=True, blank=True)
    learners_num = models.IntegerField(default=0)
    code = models.IntegerField(default=0)
    create_date = models.DateTimeField(null=True)

class ClassRoom(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    content = models.TextField()
    container_cnt = models.CharField(max_length=10)
    docker_image = models.CharField(max_length=100)
    create_date = models.DateTimeField()
    modify_date = models.DateTimeField(null=True, blank=True)
    links = models.CharField(max_length=300, null=True, blank=True)
    class_code = models.IntegerField(default=0)

    def __str__(self):
        return self.subject

class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE)
    content = models.TextField()
    create_date = models.DateTimeField()
    modify_date = models.DateTimeField(null=True, blank=True)