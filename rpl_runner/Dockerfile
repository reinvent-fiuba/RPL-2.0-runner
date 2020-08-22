FROM ubuntu:bionic

RUN apt-get update     && \
    apt-get upgrade -y && \
    apt-get install -y gcc gcc-multilib g++ clang      	\
                       make valgrind time python3.7 	\
                       libgtest-dev python3-pip

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.7 1
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.7 1

RUN pip3 install pyinstaller timeout-decorator
RUN pip3 install flask
RUN pip3 install gunicorn

RUN groupadd -g 2500 runner
RUN useradd -m -u 98989 -g runner -s /bin/bash runner

# Add runner
ADD runner-libs/ /runner-libs/

# Copy libcriterion files
RUN tar -zxvf /runner-libs/c/criterion_rpl_v2.tar.gz -C /runner-libs/c/
RUN cp -r /runner-libs/c/. /usr
RUN cp /runner-libs/python/unit_test_wrapper.py /usr

COPY ["*.py", "*_Makefile", "/"]

RUN chown -R runner:runner /home/runner

USER runner

WORKDIR /home/runner
ENTRYPOINT ["gunicorn", "--chdir", "/", "--timeout", "60", "init_server:app"]
