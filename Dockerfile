FROM ubuntu:bionic

RUN apt-get update     && \
    apt-get upgrade -y && \
    apt-get install -y gcc gcc-multilib g++ clang      	\
                       make valgrind time python3.7 	\
                       libgtest-dev

COPY ["*.py", "Makefile", "/"]

WORKDIR /tmp


ENTRYPOINT ["/usr/bin/python3.7", "/runner.py"]