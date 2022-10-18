import os
result = os.popen('docker images').read().strip().split('\n')

images_list = []

for _ in range(1, len(result)):
    print(result[_])
    result_split = result[_].split()
    images_list.append(result_split[0]+":"+result_split[1])

print(images_list)