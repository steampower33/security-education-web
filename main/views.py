from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import ClassRoom
from .forms import ClassRoomForm, CommentForm
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

def index(request):
    page = request.GET.get('page', '1')
    classroom_list = ClassRoom.objects.order_by('-create_date')
    paginator = Paginator(classroom_list, 10)

    page_obj = paginator.get_page(page)
    context = {'classroom_list': page_obj}
    return render(request, 'main/classroom_list.html', context)

def detail(request, classroom_id):
    classroom = get_object_or_404(ClassRoom, pk=classroom_id)
    context = {'classroom': classroom}
    return render(request, 'main/classroom_detail.html', context)

@login_required(login_url='accounts:login')
def comment_create(request, classroom_id):
    classroom = get_object_or_404(ClassRoom, pk=classroom_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user # author 속성에 로그인 계정 저장
            comment.create_date = timezone.now()
            comment.classroom = classroom
            comment.save()
            return redirect('main:detail', classroom_id=classroom.id)
    else:
        return HttpResponseNotAllowed('Only POST is possible.')
    context = {'classroom': classroom, 'form': form}
    return render(request, 'main/classroom_detail.html', context)

@login_required(login_url='accounts:login')
def classroom_create(request):
    if request.method == 'POST':
        form = ClassRoomForm(request.POST)
        if form.is_valid():
            classroom = form.save(commit=False)
            classroom.author = request.user # author 속성에 로그인 계정 저장
            classroom.create_date = timezone.now()
            classroom.save()
            return redirect('main:index')
    else:
        form = ClassRoomForm()
    context = {'form': form}
    return render(request, 'main/classroom_form.html', context)

