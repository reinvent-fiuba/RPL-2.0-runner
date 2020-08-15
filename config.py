import os


def flag(name, default=False):
    b = os.environ.get(name, "")
    if not b:
        return default
    return b != "0" and b.lower() != "false"


DEBUG = flag("DEBUG", False)
SYSTEMD = flag("SYSTEMD", False)

URL_RPL_BACKEND = os.environ.get("URL_RPL_BACKEND", "http://localhost:8080")
QUEUE_URL = os.environ.get("QUEUE_URL", "amqp://guest:guest@localhost:5672")
QUEUE_ACTIVITIES_NAME = os.environ.get("QUEUE_ACTIVITIES_NAME", "hello")
DOCKER_RUNNER_IMAGE = os.environ.get("DOCKER_RUNNER_IMAGE", "gcr.io/fiuba-rpl/rpl-2.0-runner:latest")
