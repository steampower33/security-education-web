import os
from collections import deque

from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import ClassRoom, Comment
from .forms import ClassRoomForm, CommentForm
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.files.storage import FileSystemStorage

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

@user_passes_test(educator_group_check, login_url='/main')
def upload(request):
    abs_path = os.getcwd().split(os.path.sep)
    media_path = '/'
    for _ in range(1, len(abs_path)):
        media_path += abs_path[_]
        media_path += '/'
    media_path += 'media/'

    image_list = os.listdir(media_path)
    result = ''
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        if str(myfile) in image_list:
            result = str(myfile) + 'is already exist in media'
            return render(request, 'docker/already.html', {'result': result})

        fs = FileSystemStorage(location='media/', base_url='media/')
        # FileSystemStorage.save(file_name, file_content)
        filename = fs.save(myfile.name, myfile)

        result = os.popen('docker load -i '+media_path+filename).read().strip().split('\n')
        result = result[0].split()

        send = ''
        load_images_path = ''
        if 'Loaded' in result:
            send = ''.join(result[1:]) + ' was created successfully.'

        return render(request, 'main/success_upload.html', {'result': send})

    return render(request, 'main/upload.html',)

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
    #print("선택된 이미지 : ", classroom.docker_image)
    #print("이미지 개수 : ", classroom.container_cnt)
    links = classroom.links.split(',')
    print(links)

    context = {'classroom': classroom, 'links':links}
    return render(request, 'main/classroom_detail.html', context)

# 컨테이너 생성
@user_passes_test(educator_group_check, login_url='/main')
def make_container(request, docker_image, container_cnt):
    f = open("main/port.txt", 'r')
    ports = deque(f.readline().split())
    f.close()

    links = ''
    for _ in range(int(container_cnt)):
        port = ports.popleft()
        cmd = 'docker run -d -p ' + port + ':80 ' + str(docker_image)
        result = os.popen(cmd)

        if _ == int(container_cnt)-1:
            links += 'http://168.188.123.173:'+port
        else:
            links += 'http://168.188.123.173:'+port+','
        print("생성된 컨테이너 : ", result.read())
    print(links)

    p = ''
    for _ in ports:
        p += _ + ' '

    print(p)

    f = open("main/port.txt", 'w')
    f.write(p)
    f.close()

    return links

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
            print("선택된 이미지 : ", classroom.docker_image)
            print("이미지 개수 : ", classroom.container_cnt)
            links = make_container(request, classroom.docker_image, classroom.container_cnt)
            classroom.links = links
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
    image_list = images() # images 정보 가져오기
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
    context = {'classroom':classroom, 'form': form, 'image_list': image_list}
    return render(request, 'main/classroom_form.html', context)

# 수업 삭제
@user_passes_test(educator_group_check, login_url='/main')
def classroom_delete(request, classroom_id):
    classroom = get_object_or_404(ClassRoom, pk=classroom_id)
    if request.user != classroom.author:
        messages.error(request, '삭제권한이 없습니다')
        return redirect('main:detail', classroom_id=classroom.id)

    ports = list()
    links = classroom.links.split(',')
    for _ in links:
        ports.append(int(_.split(':')[-1]))

    for _ in os.popen('docker ps -a').read().strip().split('\n')[1:]:
        container_id = _.split()[0]
        print("컨테이너 ID : ", container_id)

        r = os.popen('docker port '+container_id).read().strip()
        container_port = r.split(':::')[1]
        print("컨테이너 Port : ", container_port)

        print("ports : ", ports)
        p = list()
        if int(container_port) in ports:
            r = os.popen("docker rm -f "+container_id).read().strip()
            print("컨테이너 삭제 결과 : ", r)

            p.append(container_port)

    f = open("main/port.txt", 'r')
    port_file = f.readline()
    f.close()
    print(port_file)
        
    w = ''
    p += port_file.split()
    for _ in range(len(p)):
        if _ != len(p)-1:
            w += p[_]
        else:
            w += p[_] + ' '
    print(w)
    f = open("main/port.txt", 'w')
    f.write(w)
    f.close()

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