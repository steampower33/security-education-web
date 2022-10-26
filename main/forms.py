from django import forms
from main.models import ClassRoom
from main.models import Comment

class ClassRoomForm(forms.ModelForm):
    class Meta:
        model = ClassRoom
        fields = ['subject', 'content', 'container_cnt', 'docker_image']

        labels = {
            'subject': '제목',
            'content': '내용',
            'container_cnt': '컨테이너_개수',
            'docker_image': '이미지',
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        labels = {
            'content': '댓글내용',
        }
