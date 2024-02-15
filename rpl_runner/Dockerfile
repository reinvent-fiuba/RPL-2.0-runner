FROM ubuntu:jammy

RUN apt-get update     && \
    apt-get upgrade -y && \
    apt-get install -y gcc gcc-multilib g++ clang      	\
                       make valgrind time python3.10 	\
                       python3.10-dev libgtest-dev       \
                       python3-pip git

# Fix for installing flask in ubuntu:bionic
RUN apt-get install -y python3-markupsafe

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1

RUN pip3 install timeout-decorator
RUN pip3 install flask gunicorn

# Install go
RUN apt-get install -y wget
RUN wget https://go.dev/dl/go1.19.3.linux-amd64.tar.gz
RUN tar -xvf go1.19.3.linux-amd64.tar.gz
RUN mv go /usr/lib

ENV GOROOT /usr/lib/go
ENV GOCACHE /go/cache
ENV GOPATH /go
ENV PATH $GOPATH/bin:$GOROOT/bin:$PATH

RUN go version

# Create usser for main process without root privileges
RUN groupadd -g 2500 runner
RUN useradd -m -u 98989 -g runner -s /bin/bash runner

# Add runner
ADD runner-libs/ /runner-libs/

# Copy libcriterion files
RUN tar -zxvf /runner-libs/c/criterion_rpl_v2.tar.gz -C /runner-libs/c/
RUN cp -r /runner-libs/c/. /usr
RUN cp -r /runner-libs/python/. /usr

COPY ["go.mod", "go.sum", "/"]

# Cache testify dependency
RUN go get github.com/stretchr/testify@v1.7.0

# Cache testify build
RUN go install github.com/stretchr/testify

COPY ["*.py", "*_Makefile", "/"]

RUN chown -R runner:runner /home/runner
RUN chown -R runner:runner /go

ENV PYTHONUNBUFFERED=TRUE
USER runner

WORKDIR /home/runner
ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:8000", "--chdir", "/", "--timeout", "60", "init_server:app"]
