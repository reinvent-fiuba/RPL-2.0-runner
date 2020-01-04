# RPL-2.0-runner

# USAGE

Build receiver docker image:

```sh
docker build -t rpl-2.0-runner ./rpl_runner
```

## With rabbitmq

1.- Start a rabbitmq server

```sh
docker run -p 9999:15672 -p 5672:5672 deadtrickster/rabbitmq_prometheus:latest
```

2.- Start receiving messages with 

```sh
python3 rabbitmq_receive.py
```

3.- Send messages with (or just POST a submission to the RPL-server)

```sh
python3 rabbitmq_send.py <submission_id> <lang>
```

WHERE LANG can be: `python_3.7` or `c_std11`


## Without rabbitmq
```sh
docker build -t rpl-2.0-runner ./rpl_runner && python3 receiver.py <submission_id> <lang>
```

# Description

## rabbitmq_send.py
ONLY FOR TESTING: Send a message to the queue


## rabbitmq_receive.py
Receive message from queue and invoque receiver.py

## receiver.py
Get submission from RPL-Server
Creates NEW DOCKER PROCESS with a custom runner for a specific language in a docker container
Post results to RPL

## init.py, runner.py and custom_runner.py (RUNNING INSIDE DOCKER CONTAINER)
1. Prepare
2. Build
3. Run

Every step is language-specific and redirecting `stdout` and `stderr` to a tempfile.

stdout result example:
	
```json
{
    "result": "ERROR",
    "stage": "BUILD",
    "message": "Codigo Error 2",
    "stdout": "::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::BUILD OUTPUT::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::\ngcc -g -O2 -std=c99 -Wall -Wformat=2 -Wshadow -Wpointer-arith -Wunreachable-code -Wconversion -Wno-sign-conversion -Wbad-function-cast -DCORRECTOR   -c -o test_file.o test_file.c\n<builtin>: recipe for target 'test_file.o' failed\n\n::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::END BUILD OUTPUT::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::\nBUILD ERROR: error_code --> 2\n",
    "stderr": "test_file.c: In function \u2018main\u2019:\ntest_file.c:15:5: error: expected \u2018;\u2019 before \u2018tiempo_ingresado\u2019\n     tiempo_ingresado = tiempo_ingresado % 3600;\n     ^~~~~~~~~~~~~~~~\ntest_file.c:17:11: warning: conversion to \u2018float\u2019 from \u2018int\u2019 may alter its value [-Wconversion]\n     seg = tiempo_ingresado % 60;\n           ^~~~~~~~~~~~~~~~\ntest_file.c:11:5: warning: ignoring return value of \u2018scanf\u2019, declared with attribute warn_unused_result [-Wunused-result]\n     scanf (\"%d\",&tiempo_ingresado);\n     ^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\nmake: *** [test_file.o] Error 1\nmake: Target 'main' not remade because of errors.\n"
}
```


## How I tested it

In any case, you have to build the `runner` docker image that the receiver uses for testing assignments in a containerized environment.

```sh
docker build -t rpl-2.0-runner ./rpl_runner
```

Any changes made to any file inside the `rpl_runner` folder will need to rebuild the docker image.


### The hole circle
Start the rabbitmq server, the Java RPL Server and the rabbitmq_receive.py

Login, get your auth token.

Post a submission like  (replace `/home/alepox/Desktop/tp_prof/rpl/pruebita_runner/la_submission.tar.xz` and the Authorization header)

```sh
curl -X POST \
  http://localhost:8080/api/courses/1/activities/1/submissions \
  -H 'Accept: */*' \
  -H 'Accept-Encoding: gzip, deflate' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiIxIiwiaWF0IjoxNTc4MTM5MjA0LCJleHAiOjE1NzgxNTM2MDR9.nSub-DaZq5bejmN_h31gymg4xay--mbSD0_ogpGOsDJzV1pP_gkSwCF_LnwfSm0UsLFYuuoCHruC2V8hCaaIqA' \
  -H 'Cache-Control: no-cache' \
  -H 'Connection: keep-alive' \
  -H 'Content-Length: 1025' \
  -H 'Content-Type: multipart/form-data; boundary=--------------------------193299411849957077408518' \
  -H 'Host: localhost:8080' \
  -H 'Postman-Token: 66b86c8a-1d39-44fc-b2e5-309da5282640,c1af91c7-6e68-40ce-b869-02fc81afa51e' \
  -H 'User-Agent: PostmanRuntime/7.20.1' \
  -H 'cache-control: no-cache' \
  -H 'content-type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW' \
  -F file=@/home/alepox/Desktop/tp_prof/rpl/pruebita_runner/la_submission.tar.xz \
  -F 'description=files for C'
```

### Just the consumer (without using rabbitmq)
If you already have submissions in the DB and the RPL-Server is up and running.

```sh
python3 receiver.py <submission_id> <lang>
```

### Just the consumer (using rabbitmq)
If you already have submissions in the DB and the RPL-Server is up and running and the rabbitmq server too.

Enqueue a submissionId and the magic will do the rest

```sh
python3 rabbitmq_receive.py
```

```sh
python3 rabbitmq_send.py <submission_id> <lang>
```