import multiprocessing
import os

from . import utility


class Builder:
    @staticmethod
    def get_imgs():
        assert (
            utility.get_cmd_res("which docker && docker images 2>/dev/null") != None
        ), "Is docker running properly?"
        images = utility.get_cmd_res('docker images --format "{{.Repository}}"')
        images = [line for line in images.split("\n") if not line.startswith("<none>")]
        return images

    @staticmethod
    def build_img(FUZZER, TARGET, TOP_DIR, RETRY=3, BUILD_TYPE="release"):
        build_img_command = f"""
        docker build -t "{FUZZER}/{TARGET}" \
        --build-arg fuzzer_name="{FUZZER}" \
        --build-arg target_name="{TARGET}" \
        --build-arg USER_ID=$(id -u $USER) \
        --build-arg GROUP_ID=$(id -g $USER) \
        --build-arg build_type="{BUILD_TYPE}" \
        -f "{TOP_DIR}/docker/Dockerfile" \
        "{TOP_DIR}"
"""
        cnt = 0
        while cnt < RETRY:
            cnt += 1
            result = utility.get_cmd_res(build_img_command)
            if result == None:
                continue
            if len(result.strip()) == 0:
                return ""
        return f"{FUZZER}/{TARGET}"

    @staticmethod
    def wrapper_build_img(args):
        fuzzer, target, top_dir, retry, build_type = args
        return Builder.build_img(fuzzer, target, top_dir, retry, build_type)

    @staticmethod
    @utility.time_count("Build images done")
    def build_imgs(FUZZERS, TARGETS, RETRY=3, BUILD_TYPE="release"):
        Builder.RETRY = RETRY
        top_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        failed = []
        targets = TARGETS if type(TARGETS) != dict else list(TARGETS.keys())
        images = Builder.get_imgs()
        with multiprocessing.Pool() as pool:
            results = pool.imap_unordered(
                Builder.wrapper_build_img,
                [
                    (fuzzer, targets[0], top_dir, 1, BUILD_TYPE)
                    for fuzzer in FUZZERS
                    if f"{fuzzer}/{targets[0]}" not in images
                ],
            )
            for result in results:
                pass
        images = Builder.get_imgs()
        with multiprocessing.Pool() as pool:
            results = pool.imap_unordered(
                Builder.wrapper_build_img,
                [
                    (fuzzer, target, top_dir, RETRY, BUILD_TYPE)
                    for fuzzer in FUZZERS
                    for target in targets
                    if f"{fuzzer}/{target}" not in images
                ],
            )
            for result in results:
                result = result.strip()
                if len(result) > 0:
                    failed.append(result)
        if len(failed) > 0:
            utility.console.print(
                f"[bold red]Failed to build {len(failed)} images: [/bold red]"
            )
            utility.console.print(f'[bold]{" ".join(failed)}[/bold]')
        return failed
