from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
import os

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

        return render(request, 'docker/success_upload.html', {'result': send})

    return render(request, 'docker/upload.html',)

def images(request):
    result = os.popen('docker images').read().strip().split('\n')

    image_list = []

    for _ in range(1, len(result)):
        print(result[_])
        result_split = result[_].split()
        image_list.append(result_split[0])

    print(image_list)

    return render(request, 'docker/images.html', {'image_list': image_list})

def make_container(request):
    image = request.POST.get('image')
    print('docker run -d -p 8081:80 ' + image)
    result =  ''
    result1 = os.popen('docker run --name web1 -d -p 8081:80 ' + image)
    result2 = os.popen('docker run -d --name web2 -p 8082:80 ' + image)
    result3 = os.popen('docker run -d --name web3 -p 8083:80 ' + image)

    result = result1.read()[:13]+","+result2.read()[:13]+","+result3.read()[:13]+" was created successfully"
    print(result)

    return render(request, 'docker/make_container.html', {'result': result})