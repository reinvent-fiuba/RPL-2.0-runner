#!/bin/sh

dockerd &> dockerd-logfile &     # Start docker daemon
# Wait for docker daemon
while (! docker stats --no-stream ); do
  sleep 1
done
echo "Loading rpl-2.0-runner:latest image from rpl-2.0-runner_latest.tar.gz"
docker load < /app/rpl-2.0-runner_latest.tar.gz

docker image ls

touch /tmp/healthy  # so that readiness probe is aware that we are ready to receive traffic / start consumming

python3 -u rabbitmq_receive.py