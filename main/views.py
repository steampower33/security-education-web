import os
from collections import deque

from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import ClassRoom, Comment, Classes
from .forms import ClassRoomForm, CommentForm, ClassesForm
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
    if request.method == 'POST' and 'myfile' in request.FILES:
        myfile = request.FILES['myfile']
        if str(myfile) in image_list:
            result = str(myfile) + 'is already exist in media'
            return render(request, 'main/already.html', {'result': result})

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

# 게시글 목록
def post_list(request, class_code):
    page = request.GET.get('page', '1')

    classroom_list = ClassRoom.objects.order_by('-create_date').filter(class_code=class_code)
    paginator = Paginator(classroom_list, 10)

    print(class_code)

    page_obj = paginator.get_page(page)
    context = {'classroom_list': page_obj, 'class_code':class_code}
    return render(request, 'main/classroom_post_list.html', context)

# 수업 목록
def class_list(request):
    is_educator = False
    is_learner = False
    print(request.user.groups.all())
    for g in request.user.groups.all():
        if g.name == 'educator':
            is_educator = True
        if g.name == 'learner':
            is_learner = True
    
    if is_learner:
        attend_class_info = list()
        for c in Classes.objects.all():
            info = dict()
            if c.learners:
                if str(request.user) in c.learners:
                    #print(request.user,"는 ",c.class_name,"에 등록되어있습니다.")
                    # 교육자, 수업 이름, 현재 학습자 / 총 학습자
                    info['educator'] = str(c.educator)
                    info['class_name'] = str(c.class_name)
                    info['learners_num'] = str(c.learners_num)
                    info['max_learner'] = str(c.max_learner)
                    info['id'] = int(c.id)
                    info['code'] = int(c.code)
                if not info:
                    print("?")
                else:
                    attend_class_info.append(info)
                    #print(attend_class_info)
    elif is_educator:
        attend_class_info = list()
        for c in Classes.objects.all():
            info = dict()
            if str(c.educator) == str(request.user):
                #print(request.user,"는 ",c.class_name,"에 등록되어있습니다.")
                # 교육자, 수업 이름, 현재 학습자 / 총 학습자
                info['educator'] = str(c.educator)
                info['class_name'] = str(c.class_name)
                info['learners_num'] = str(c.learners_num)
                info['max_learner'] = str(c.max_learner)
                info['id'] = int(c.id)
                info['code'] = int(c.code)
            if not info:
                print("?")
            else:
                attend_class_info.append(info)
                #print(attend_class_info)

    context = {'attend_class_info': attend_class_info, 'is_educator': is_educator, 'is_learner': is_learner}
    return render(request, 'main/class_list.html', context)

# 모든 수업 확인(관리자용)
def class_list_all(request):
    page = request.GET.get('page', '1')
    class_list = Classes.objects.order_by('-create_date')
    paginator = Paginator(class_list, 10)

    page_obj = paginator.get_page(page)
    context = {'class_list': page_obj}
    return render(request, 'main/class_list_all.html', context)

# 수업 생성
@user_passes_test(educator_group_check, login_url='/main')
def class_create(request):
    if request.method == 'POST':
        # 중복되는 코드의 수업 존재 유무 체크
        r_code = request.POST['code']
        for c in Classes.objects.all():
            print("등록하려는 수업의 코드 : ", r_code)
            print("c의 수업 코드", c.code)
            if c.code == int(r_code):
                print("중복되는 코드의 수업이 이미 존재합니다.")
                return redirect('main:index')
        form = ClassesForm(request.POST)
        if form.is_valid():
            classes = form.save(commit=False)
            classes.educator = request.user # author 속성에 로그인 계정 저장
            classes.create_date = timezone.now()
            classes.save()
            return redirect('main:index')
    else:
        form = ClassesForm()
    context = {'form': form}
    return render(request, 'main/class_create.html', context)

# 수업 삭제
def class_delete(request, class_code):
    print("수업 삭제 구현중")
    print("수업 코드는 ",class_code)
    for c in ClassRoom.objects.all():
        print("이 게시물의 수업 코드는", c.class_code)
        if class_code == c.class_code:
            print("코드가 일치합니다. 해당 게시물을 삭제합니다.")
            classroom_delete(request, c.id)

    Class = get_object_or_404(Classes, code=class_code)
    Class.delete()
    return redirect('main:class_list')

# 수업 참가
def class_attend(request):
    if request.method == 'POST':
        r_code = request.POST['code']
        print("등록하려는 수업의 코드 : ", r_code)
        for c in Classes.objects.all():
            print(c,"의 코드는",c.code)
            if c.code == int(r_code):
                print("코드가 동일합니다.")
                l = c.learners
                if l:
                    c.learners = l + " " + str(request.user)
                else:
                    c.learners = str(request.user)
                c.learners_num = len(c.learners.split())
                c.save()
        return redirect('main:index')

    return render(request, 'main/class_attend.html')

# 메인 페이지
def index(request):
    return render(request, 'index.html')

# 수업 내용
def detail(request, classroom_id):
    classroom = get_object_or_404(ClassRoom, pk=classroom_id)
    #print("선택된 이미지 : ", classroom.docker_image)
    #print("이미지 개수 : ", classroom.container_cnt)
    links = classroom.links.split(',')
    print("컨테이너 주소 : ", links)
    print("게시글 코드 : ", classroom.class_code)

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

# 수업 게시글 생성
@user_passes_test(educator_group_check, login_url='/main')
def classroom_create(request, class_code):
    image_list = images() # images 정보 가져오기
    if request.method == 'POST':
        form = ClassRoomForm(request.POST)
        if form.is_valid():
            classroom = form.save(commit=False)
            classroom.author = request.user # author 속성에 로그인 계정 저장
            classroom.create_date = timezone.now()
            classroom.class_code = class_code
            print("선택된 이미지 : ", classroom.docker_image)
            print("이미지 개수 : ", classroom.container_cnt)
            links = make_container(request, classroom.docker_image, classroom.container_cnt)
            classroom.links = links
            classroom.save()
            return redirect('main:post_list', class_code=class_code)
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

# 수업 게시글 수정
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

# 수업 게시글 삭제
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
        container_port = r.split(':')[1]
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
            w += p[_] + ' '
        else:
            w += p[_]
    print(w)
    f = open("main/port.txt", 'w')
    f.write(w)
    f.close()

    classroom.delete()
    return redirect('main:post_list', class_code=classroom.class_code)

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