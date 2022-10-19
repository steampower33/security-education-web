from django import forms
from main.models import ClassRoom
from main.models import Comment

class ClassRoomForm(forms.ModelForm):
    class Meta:
        model = ClassRoom
        fields = ['subject', 'content']

        labels = {
            'subject': '제목',
            'content': '내용',
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        labels = {
            'content': '답변내용',
        }
