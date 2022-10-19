from django.urls import path

from . import views

app_name = 'main'

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:classroom_id>/', views.detail, name='detail'),
    path('comment/create/<int:classroom_id>/', views.comment_create, name='comment_create'),
    path('classroom/create/', views.classroom_create, name='classroom_create'),
    path('<int:classroom_id>/modify', views.classroom_modify, name='classroom_modify'),
    path('classroom/delete/<int:classroom_id>/', views.classroom_delete, name='classroom_delete'),
]