# RPL-2.0-runner

## USAGE

### With rabbitmq

1.- Start a rabbitmq server

```
docker run -p 9999:15672 -p 5672:5672 deadtrickster/rabbitmq_prometheus:latest
```

2.- Start receiving messages with 

```
python3 rabbitmq_receive.py
```

3.- Send messages with 

```
python3 rabbitmq_send.py <submission_id>
```

## rabbitmq_send.py
	ONLY FOR TESTING: Send a message to the queue


## rabbitmq_receive.py
	Receive message from queue and invoque receiver.py

## receiver.py
	Get submission from RPL
	invoques NEW DOCKER PROCESS with a custom runner for a language in a docker container
	Post results to RPL

## runner.py and runner_c.py (RUNNING INSIDE DOCKER CONTAINER)
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

