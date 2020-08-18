# FROM python:3.8

# # https://github.com/jpetazzo/dind/blob/master/Dockerfile

# # Let's start with some basic stuff.
# RUN apt-get update -qq && apt-get install -qqy \
#     apt-transport-https \
#     ca-certificates \
#     curl \
#     lxc \
#     iptables
    
# # Install Docker from Docker Inc. repositories.
# RUN curl -sSL https://get.docker.com/ | sh

# RUN apt-get update     && \
#     apt-get upgrade -y && \
#     apt-get install -y python3-dev && \
#     apt-get install -y libsystemd-dev

# WORKDIR /app

# COPY requirements.txt ./

# RUN pip install -r requirements.txt

# COPY . ./

# ENTRYPOINT ["python3", "-u", "rabbitmq_receive.py"]

FROM docker:dind

RUN apk update     && \
    apk add python3 python3-dev py3-pip
    # apk add libsystemd-dev

WORKDIR /app

COPY requirements.txt ./

RUN pip3 install -r requirements.txt

# COPY rpl-2.0-runner_latest.tar.gz ./

COPY . ./

# RUN chmod a+x /app/entrypoint.sh

ENTRYPOINT ["python3", "-u", "rabbitmq_receive.py"]