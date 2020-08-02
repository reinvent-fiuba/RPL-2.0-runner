dockerd &> dockerd-logfile &     # Start docker daemon
# Wait for docker daemon
while (! docker stats --no-stream ); do
  sleep 1
done
docker pull $DOCKER_RUNNER_IMAGE # Pull runner image
