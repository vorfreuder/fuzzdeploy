import docker
from docker.errors import DockerException

from . import aflcov, casr, fuzzer_state, vulnerability_detection_time
from .build import build_fuzzer, build_image, build_images, build_target
from .deploy import fuzzing
from .utils import work_dir_iterdir

try:
    docker.from_env().ping()
except DockerException:
    assert False, "Is docker running properly?"
