env : python3.6, docker20.10.7, docker-compose1.29.2

------------------------------------------------------------

container up
```
$ docker-compose -f docker-compose.prod.yml up --build -d
$ docker-compose -f docker-compose.prod.yml up -d
```

container down
```
$ docker-compose -f docker-compose.prod.yml down -v
$ docker-compose -f docker-compose.prod.yml down
```

container logs
```
$ docker-compose -f docker-compose.prod.yml logs -f
```

------------------------------------------------------------

web logs : /home/ubuntu/code/web_nicework/nicework/logs
