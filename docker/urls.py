from django.urls import path
from . import views

app_name = 'docker'

urlpatterns = [
    path('upload/', views.upload, name='upload'),
    path('images/', views.images, name='images'),
    path('make_container/', views.make_container, name='make_container'),
]