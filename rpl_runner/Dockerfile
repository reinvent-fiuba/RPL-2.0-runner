FROM ubuntu:bionic

RUN apt-get update     && \
    apt-get upgrade -y && \
    apt-get install -y gcc gcc-multilib g++ clang      	\
                       make valgrind time python3.7 	\
                       libgtest-dev python3-pip

RUN pip3 install pyinstaller timeout-decorator
RUN pip3 install flask
RUN pip3 install gunicorn
# Add runner
ADD runner-libs/ /runner-libs/

# Copy libcriterion files
#RUN tar -zxvf /runner-libs/c/criterion-v2.3.0-rc2-custom.tar.gz -C /runner-libs/c/
#RUN cp -r /runner-libs/c/criterion-v2.3.0-rc2/. /usr

RUN tar -zxvf /runner-libs/c/criterion_rpl_v2.tar.gz -C /runner-libs/c/
RUN cp -r /runner-libs/c/. /usr
RUN cp /runner-libs/python/unit_test_wrapper.py /usr

COPY ["*.py", "*_Makefile", "/"]


ENTRYPOINT ["gunicorn", "init_server:app"]