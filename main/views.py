from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import ClassRoom, Comment
from .forms import ClassRoomForm, CommentForm
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
import os

# educator 접근 권한
def educator_group_check(user):
    for _ in user.groups.all():
        if _.name == 'educator':
            print("Hello, educator")
            return True
    return False

def images():
    result = os.popen('docker images').read().strip().split('\n')

    image_list = []

    for _ in range(1, len(result)):
        print(result[_])
        result_split = result[_].split()
        image_list.append(result_split[0])

    print(image_list)

    return image_list

# 수업 목록
def index(request):
    page = request.GET.get('page', '1')
    classroom_list = ClassRoom.objects.order_by('-create_date')
    paginator = Paginator(classroom_list, 10)

    page_obj = paginator.get_page(page)
    context = {'classroom_list': page_obj}
    return render(request, 'main/classroom_list.html', context)

# 수업 내용
def detail(request, classroom_id):
    classroom = get_object_or_404(ClassRoom, pk=classroom_id)
    context = {'classroom': classroom}
    return render(request, 'main/classroom_detail.html', context)

# 수업 생성
@user_passes_test(educator_group_check, login_url='/main')
def classroom_create(request):
    image_list = images() # images 정보 가져오기
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
    context = {'form': form, 'image_list': image_list}
    return render(request, 'main/classroom_form.html', context)

# 댓글 생성
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

# 수업 수정
@user_passes_test(educator_group_check, login_url='/main')
def classroom_modify(request, classroom_id):
    classroom = get_object_or_404(ClassRoom, pk=classroom_id)
    if request.user != classroom.author:
        messages.error(request, '수정권한이 없습니다')
        return redirect('main:detail', classroom_id=classroom.id)

    if request.method == 'POST':
        form = ClassRoomForm(request.POST, instance=classroom)
        if form.is_valid():
            classroom = form.save(commit=False)
            classroom.modify_date = timezone.now()
            classroom.save()
            return redirect('main:detail', classroom_id=classroom.id)
    else:
        form = ClassRoomForm(instance=classroom)
    context = {'classroom':classroom, 'form': form}
    return render(request, 'main/classroom_form.html', context)

# 수업 삭제
@user_passes_test(educator_group_check, login_url='/main')
def classroom_delete(request, classroom_id):
    classroom = get_object_or_404(ClassRoom, pk=classroom_id)
    if request.user != classroom.author:
        messages.error(request, '삭제권한이 없습니다')
        return redirect('main:detail', classroom_id=classroom.id)
    classroom.delete()
    return redirect('main:index')

# 댓글 수정
@login_required(login_url='common:login')
def comment_modify(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user != comment.author:
        messages.error(request, '수정권한이 없습니다')
        return redirect('main:detail', classroom_id=comment.classroom.id)

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.modify_date = timezone.now()
            comment.save()
            return redirect('main:detail', classroom_id=comment.classroom.id)
    else:
        form = CommentForm(instance=comment)
    context = {'comment': comment, 'form': form}
    return render(request, 'main/comment_form.html', context)

# 댓글 삭제
@login_required(login_url='accounts:login')
def comment_delete(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user != comment.author:
        messages.error(request, '삭제권한이 없습니다')
    else:
        comment.delete()
    return redirect('main:detail', classroom_id=comment.classroom.id)