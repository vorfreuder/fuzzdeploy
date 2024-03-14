import os
import sys

import psutil

from fuzzdeploy import Builder, Deployer

FUZZERS = [
    "afl",  # not support: imagemagick
    "aflplusplus",
    # "memlock",  # not support: imagemagick
    # "tortoisefuzz",
]
TARGETS = {
    # "bento4": "mp42hls @@",
    # "binutils": "readelf -w @@",
    # "boolector": "boolector @@",
    # "bzip2": "bzip2recover @@",
    # "cflow": "cflow @@",
    # "cxxfilt": "cxxfilt -t",
    # "exiv2": "exiv2 -pX @@",
    # "flex": "flex @@",
    # "gifsicle": "gifsicle @@ test.gif -o /dev/null",
    # "gpac": "MP4Box -diso @@ -out /dev/null",
    # "gpac_latest": "MP4Box -hint @@",
    # "graphicsmagick": "gm identify @@",
    # "imagemagick": "convert @@ /dev/null",
    # "jasper": "jasper -f @@ -t mif -F /dev/null -T jpg",
    # "jpegoptim": "jpegoptim @@",
    # "libxml2": "xmllint -o /dev/null @@",
    # "lrzip": "lrzip -t @@",
    "mjs": "mjs -f @@",
    # "mxml": "mxmldoc @@",
    # "nasm": "nasm -f bin @@ -o ./tmp",
    # "nasm_2.16.01": "nasm -f bin @@ -o ./tmp",
    # "nm": "nm -C @@",
    # "openh264": "h264dec @@ ./tmp",
    # "openjpeg": "opj_decompress -i @@ -o ./tmp.png",
    # "readelf": "readelf -a @@",
    # "rec2csv": "rec2csv @@",
    # "yaml-cpp": "parse @@",
    # "yara": "yara @@ strings",
    "yasm": "yasm @@",
}
WORK_DIR = (
    sys.argv[1]
    if len(sys.argv) > 1
    else os.path.join(os.path.dirname(os.path.realpath(__file__)), "workdir_test")
)
REPEAT = 1
TIMEOUT = "5m"
CPU_NUM = psutil.cpu_count()
if CPU_NUM > 50:
    CPU_NUM -= 6
elif CPU_NUM > 2:
    CPU_NUM -= 2
CPU_RANGE = [str(i) for i in range(CPU_NUM)]
skip_det = True
mopt = False
FUZZERS_ARGS = {}
for fuzzer in FUZZERS:
    FUZZERS_ARGS[fuzzer] = {}
    for target in TARGETS.keys():
        fuzzerargs = ""
        if "aflplusplus" in fuzzer:
            if not skip_det:
                fuzzerargs += "-D "
            if mopt:
                fuzzerargs += "-L 1 "
        elif fuzzer in ["afl", "memlock", "mopt", "tortoisefuzz"]:
            if skip_det:
                fuzzerargs += "-d "
        FUZZERS_ARGS[fuzzer][target] = fuzzerargs.strip()

# build docker images
Builder.build_imgs(FUZZERS=FUZZERS + ["casr"], TARGETS=TARGETS)
# fuzzing
Deployer.start_fuzzing(
    WORK_DIR=WORK_DIR,
    FUZZERS=FUZZERS,
    TARGETS=TARGETS,
    TIMEOUT=TIMEOUT,
    FUZZERS_ARGS=FUZZERS_ARGS,
    REPEAT=REPEAT,
    CPU_RANGE=CPU_RANGE,
)
