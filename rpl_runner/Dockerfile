FROM ubuntu:bionic

RUN apt-get update     && \
    apt-get upgrade -y && \
    apt-get install -y gcc gcc-multilib g++ clang      	\
                       make valgrind time python3.7 	\
                       python3.7-dev libgtest-dev       \
                       python3-pip

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.7 1
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.7 1

RUN pip3 install pyinstaller timeout-decorator
RUN pip3 install flask gunicorn
RUN pip3 install pandas
RUN pip3 install numpy
RUN pip3 install scikit-learn

# Create usser for main process without root privileges 
RUN groupadd -g 2500 runner
RUN useradd -m -u 98989 -g runner -s /bin/bash runner

# Add runner
ADD runner-libs/ /runner-libs/

# Copy libcriterion files
RUN tar -zxvf /runner-libs/c/criterion_rpl_v2.tar.gz -C /runner-libs/c/
RUN cp -r /runner-libs/c/. /usr
RUN cp /runner-libs/python/unit_test_wrapper.py /usr
RUN cp /runner-libs/python/custom_compileall.py /usr

COPY ["*.py", "*_Makefile", "/"]

RUN chown -R runner:runner /home/runner

ENV PYTHONUNBUFFERED=TRUE
USER runner

WORKDIR /home/runner
ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:8000", "--chdir", "/", "--timeout", "60", "init_server:app"]
