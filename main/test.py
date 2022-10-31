#53 82 110 111 143 443 444 554 1047 1521 1755 2401 3690 5555 5900 7777 8000 8001 8002 8010 8081 8082 8083 8090 8888 9001 9040 9050 9071 9080 9090 9101 9102 9998
from collections import deque
import os

docker_image = 'nginx'
container_cnt = 3

f = open("./port.txt", 'r')
ports = deque(f.readline().split())
f.close()

for _ in range(container_cnt):
    cmd = 'docker run -d -p ' + ports.popleft() + ':80 ' + str(docker_image)
    print(cmd)

p = ''
for _ in ports:
    p += _
    p += " "

print(p)

f = open("./port.txt", 'w')
f.write(p)
f.close()

result = os.popen('docker ps -a').read().strip().split('\n')[1:][0].split()[0]
print(result)

r = os.popen('docker port '+result).read().strip()
print(r.split(':')[1])
