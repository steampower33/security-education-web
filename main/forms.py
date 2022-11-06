from django import forms
from main.models import ClassRoom, Comment, Classes

class ClassRoomForm(forms.ModelForm):
    class Meta:
        model = ClassRoom
        fields = ['subject', 'content', 'container_cnt', 'docker_image', 'links']

        labels = {
            'subject': '제목',
            'content': '내용',
            'container_cnt': '컨테이너_개수',
            'docker_image': '이미지',
            'links': '컨테이너링크',
        }

class ClassesForm(forms.ModelForm):
    class Meta:
        model = Classes
        fields = ['class_name', 'max_learner', 'learners', 'code']

        labels = {
            'class_name': '수업 이름',
            'max_learner': '최대 학생수',
            'learners': '학생 명단',
            'code': '수업 코드',
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        labels = {
            'content': '댓글내용',
        }
