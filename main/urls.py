from django.urls import path

from . import views

app_name = 'main'

urlpatterns = [
    path('', views.index, name='index'),
    path('class/class_list', views.class_list, name='class_list'),
    path('class/class_list_all', views.class_list_all, name='class_list_all'),
    path('class/class_produce', views.class_produce, name='class_produce'),
    path('class/class_attend', views.class_attend, name='class_attend'),
    path('post_list/', views.post_list, name='post_list'),
    path('<int:classes_id>/post_list/', views.post_list, name='post_list'),
    path('<int:classroom_id>/', views.detail, name='detail'),
    path('comment/create/<int:classroom_id>/', views.comment_create, name='comment_create'),
    path('classroom/create/', views.classroom_create, name='classroom_create'),
    path('classroom/modify/<int:classroom_id>/', views.classroom_modify, name='classroom_modify'),
    path('classroom/delete/<int:classroom_id>/', views.classroom_delete, name='classroom_delete'),
    path('comment/modify/<int:comment_id>/', views.comment_modify, name='comment_modify'),
    path('comment/delete/<int:comment_id>/', views.comment_delete, name='comment_delete'),
    path('upload/', views.upload, name='upload'),
]