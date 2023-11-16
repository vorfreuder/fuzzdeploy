import multiprocessing
import os

from . import utility


class Builder:
    RETRY = None

    @staticmethod
    def retry(command):
        cnt = 0
        while cnt < Builder.RETRY:
            cnt += 1
            result = utility.get_cmd_res(command)
            if len(result.strip()) == 0:
                return ""
        return result

    @staticmethod
    @utility.time_count("Build images done")
    def build_imgs(FUZZERS, TARGETS, RETRY=2, BUILD_TYPE="release"):
        Builder.RETRY = RETRY + 1
        top_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        failed = []
        images = utility.get_cmd_res('docker images --format "{{.Repository}}"')
        images = [line for line in images.split("\n") if not line.startswith("<none>")]
        targets = TARGETS if type(TARGETS) != dict else list(TARGETS.keys())
        with multiprocessing.Pool() as pool:
            results = pool.imap_unordered(
                utility.get_cmd_res,
                [
                    f"""
        docker build -t "{fuzzer}/{targets[0]}" \
        --build-arg fuzzer_name="{fuzzer}" \
        --build-arg target_name="{targets[0]}" \
        --build-arg USER_ID=$(id -u $USER) \
        --build-arg GROUP_ID=$(id -g $USER) \
        --build-arg build_type="{BUILD_TYPE}" \
        -f "{top_dir}/docker/Dockerfile" \
        "{top_dir}" \
        || echo {fuzzer}/{targets[0]}
"""
                    for fuzzer in FUZZERS
                    if f"{fuzzer}/{targets[0]}" not in images
                ],
            )
            for result in results:
                pass
        images = utility.get_cmd_res('docker images --format "{{.Repository}}"')
        images = [line for line in images.split("\n") if not line.startswith("<none>")]
        with multiprocessing.Pool() as pool:
            results = pool.imap_unordered(
                Builder.retry,
                [
                    f"""
    docker build -t "{fuzzer}/{target}" \
    --build-arg fuzzer_name="{fuzzer}" \
    --build-arg target_name="{target}" \
    --build-arg USER_ID=$(id -u $USER) \
    --build-arg GROUP_ID=$(id -g $USER) \
    --build-arg build_type="{BUILD_TYPE}" \
    -f "{top_dir}/docker/Dockerfile" \
    "{top_dir}" \
    || echo {fuzzer}/{target}
"""
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
            utility.console.print("[bold red]Failed to build images: [/bold red]")
            utility.console.print(f'[bold]{" ".join(failed)}[/bold]')
        return failed
