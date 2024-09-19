import docker
from docker.errors import DockerException

from .build import build_fuzzer, build_image, build_images, build_target
from .deploy import fuzzing

try:
    docker.from_env().ping()
except DockerException:
    assert False, "Is docker running properly?"
