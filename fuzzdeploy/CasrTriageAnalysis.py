import os
import re

from openpyxl.styles import Font, PatternFill

from . import utility
from .Builder import Builder
from .CPUAllocator import CPUAllocator
from .ExcelManager import ExcelManager
from .utility import MEMORY_RELATED_BUGS


class CasrTriageAnalysis:
    fuzzer_colors = {
        "aflplusplus": "00A0B0",
        "htfuzz": "FBD26A",
    }
    display_fields = [
        "fuzzer",
        "repeat",
        "unique_line",
        "casr_dedup",
        "casr_dedup_cluster",
    ]
    Severity = {
        "EXPLOITABLE": (
            "SegFaultOnPc",
            "ReturnAv",
            "BranchAv",
            "CallAv",
            "DestAv",
            "BranchAvTainted",
            "CallAvTainted",
            "DestAvTainted",
            "heap-buffer-overflow(write)",
            "global-buffer-overflow(write)",
            "stack-use-after-scope(write)",
            "stack-use-after-return(write)",
            "stack-buffer-overflow(write)",
            "stack-buffer-underflow(write)",
            "heap-use-after-free(write)",
            "container-overflow(write)",
            "param-overlap",
        ),
        "PROBABLY_EXPLOITABLE": (
            "BadInstruction",
            "SegFaultOnPcNearNull",
            "BranchAvNearNull",
            "CallAvNearNull",
            "HeapError",
            "StackGuard",
            "DestAvNearNull",
            "heap-buffer-overflow",
            "global-buffer-overflow",
            "stack-use-after-scope",
            "use-after-poison",
            "stack-use-after-return",
            "stack-buffer-overflow",
            "stack-buffer-underflow",
            "heap-use-after-free",
            "container-overflow",
            "negative-size-param",
            "calloc-overflow",
            "readllocarray-overflow",
            "pvalloc-overflow",
            "overwrites-const-input",
        ),
        "NOT_EXPLOITABLE": (
            "SourceAv",
            "AbortSignal",
            "AccessViolation",
            "SourceAvNearNull",
            "SafeFunctionCheck",
            "FPE",
            "StackOverflow",
            "double-free",
            "bad-free",
            "alloc-dealloc-mismatch",
            "heap-buffer-overflow(read)",
            "global-buffer-overflow(read)",
            "stack-use-after-scope(read)",
            "stack-use-after-return(read)",
            "stack-buffer-overflow(read)",
            "stack-buffer-underflow(read)",
            "heap-use-after-free(read)",
            "container-overflow(read)",
            "initialization-order-fiasco",
            "new-delete-type-mismatch",
            "bad-malloc_usable_size",
            "odr-violation",
            "memory-leaks",
            "invalid-allocation-alignment",
            "invalid-aligned-alloc-alignment",
            "invalid-posix-memalign-alignment",
            "allocation-size-too-big",
            "out-of-memory",
            "fuzz target exited",
            "timeout",
        ),
    }

    @staticmethod
    def is_memory_related_bug(bug_type):
        return bug_type not in (
            "param-overlap",
            "BadInstruction",
            "overwrites-const-input",
            "AbortSignal",
            "SafeFunctionCheck",
            "FPE",
            "initialization-order-fiasco",
            "odr-violation",
            "fuzz target exited",
            "timeout",
        )

    @staticmethod
    @utility.time_count("CRASH TRIAGE BY CASR@https://github.com/ispras/casr DONE!")
    def triage_by_casr(WORK_DIR):
        assert os.path.exists(WORK_DIR), f"{WORK_DIR} not exists"
        WORK_DIR_TRIAGE_BY_CASR = os.path.join(WORK_DIR, "triage_by_casr")
        # check if images exist
        TARGETS = set()
        for test_path in utility.get_workdir_paths(WORK_DIR):
            fuzzer, target, repeat = utility.parse_path_by(test_path)
            TARGETS.add(target)
        Builder.build_imgs(FUZZERS=["casr"], TARGETS=list(TARGETS))

        # calculate crashes sum
        def get_triaged_crashes_num(triaged_path):
            triaged_num = 0
            if os.path.exists(os.path.join(triaged_path, "failed")):
                triaged_num += len(os.listdir(os.path.join(triaged_path, "failed")))
            if os.path.exists(os.path.join(triaged_path, "reports")):
                triaged_num += len(os.listdir(os.path.join(triaged_path, "reports")))
            return triaged_num

        crashes_sum = {}
        current_crashes_num = {}
        untriaged_paths = []
        for test_path in utility.get_workdir_paths(WORK_DIR):
            assert os.path.exists(
                os.path.join(test_path, "target_args")
            ), f"target_args not found in {test_path}"
            fuzzer_stats_path = utility.search_file(test_path, "fuzzer_stats")
            if fuzzer_stats_path is None:
                utility.console.print(
                    f"[yellow]Warning: fuzzer_stats not found in {test_path}, maybe fine.[/yellow]"
                )
            fuzzer, target, repeat = utility.parse_path_by(test_path)
            triage_by_casr = os.path.join(
                WORK_DIR_TRIAGE_BY_CASR, fuzzer, target, repeat
            )
            triaged_num = get_triaged_crashes_num(triage_by_casr)
            for foldername, subfolders, filenames in os.walk(test_path):
                if "crashes" in subfolders:
                    files = os.listdir(os.path.join(foldername, "crashes"))
                    if "README.txt" in files:
                        files.remove("README.txt")
                    fuzzer, target, repeat = utility.parse_path_by(test_path)
                    crashes_sum[f"{fuzzer}/{target}/{repeat}"] = len(files)
                    break
            if f"{fuzzer}/{target}/{repeat}" not in crashes_sum:
                continue
            if triaged_num != crashes_sum[f"{fuzzer}/{target}/{repeat}"]:
                untriaged_paths.append(test_path)
            elif triaged_num == 0 and (
                not os.path.exists(
                    os.path.join(triage_by_casr, "summary_by_unique_line")
                )
            ):
                untriaged_paths.append(test_path)

        with utility.Progress(
            utility.SpinnerColumn(spinner_name="arrow3"),
            utility.TextColumn("[progress.description]{task.description}"),
            utility.BarColumn(),
            utility.TextColumn("[bold]{task.completed} / {task.total}"),
            utility.TimeElapsedColumn(),
            transient=True,
        ) as progress:
            cpu_allocator = CPUAllocator()
            last_triaged_crashes_num = 0

            def update_progress(progress, last_triaged_crashes_num):
                for test_path in untriaged_paths:
                    fuzzer, target, repeat = utility.parse_path_by(test_path)
                    triage_by_casr = os.path.join(
                        WORK_DIR_TRIAGE_BY_CASR, fuzzer, target, repeat
                    )
                    if crashes_sum[
                        f"{fuzzer}/{target}/{repeat}"
                    ] == current_crashes_num.get(f"{fuzzer}/{target}/{repeat}", 0):
                        continue
                    current_crashes_num[
                        f"{fuzzer}/{target}/{repeat}"
                    ] = get_triaged_crashes_num(triage_by_casr)
                triaged_crashes_num = sum(current_crashes_num.values())
                progress.update(
                    triage_task,
                    advance=triaged_crashes_num - last_triaged_crashes_num,
                )
                return triaged_crashes_num

            triage_task = progress.add_task(
                "[bold green]Triaging", total=sum(crashes_sum.values())
            )
            for test_path in untriaged_paths:
                fuzzer, target, repeat = utility.parse_path_by(test_path)
                triage_by_casr = os.path.join(
                    WORK_DIR_TRIAGE_BY_CASR, fuzzer, target, repeat
                )
                os.makedirs(triage_by_casr, exist_ok=True)
                while True:
                    cpu_id = cpu_allocator.get_free_cpu(sleep_time=1, time_out=10)
                    last_triaged_crashes_num = update_progress(
                        progress, last_triaged_crashes_num
                    )
                    if cpu_id is not None:
                        break
                container_id = utility.get_cmd_res(
                    f"""
            docker run \
            -itd \
            --rm \
            --volume={test_path}:/shared \
            --volume={triage_by_casr}:/triage_by_casr \
            --cap-add=SYS_PTRACE \
            --security-opt seccomp=unconfined \
            --cpuset-cpus="{cpu_id}" \
            --network=none \
            "casr/{target}" \
            -c '${{SRC}}/triage_by_casr.sh'
                    """
                ).strip()
                cpu_allocator.append(container_id, cpu_id)
            while len(cpu_allocator.container_id_dict) > 0:
                last_triaged_crashes_num = update_progress(
                    progress, last_triaged_crashes_num
                )
                cpu_id = cpu_allocator.get_free_cpu(sleep_time=5, time_out=10)
                if cpu_id is None:
                    continue
                container_id_dict = cpu_allocator.container_id_dict
                if len(container_id_dict) == 0:
                    break
                min_container_id = min(
                    container_id_dict, key=lambda k: len(container_id_dict[k])
                )
                allocated_cpu_ls = cpu_allocator.append(min_container_id, cpu_id)
                utility.get_cmd_res(
                    f"docker update --cpuset-cpus {','.join(allocated_cpu_ls)} {min_container_id} 2>/dev/null"
                )
        triage_results = {}
        for test_path in utility.get_workdir_paths(WORK_DIR):
            fuzzer, target, repeat = utility.parse_path_by(test_path)
            triage_by_casr = os.path.join(
                WORK_DIR_TRIAGE_BY_CASR, fuzzer, target, repeat
            )
            triage = {
                "fuzzer": fuzzer,
                "repeat": repeat,
                "unique_line": 0,
                "casr_dedup": 0,
                "casr_dedup_cluster": 0,
            }
            if os.path.exists(os.path.join(triage_by_casr, "reports_dedup")):
                triage["casr_dedup"] = len(
                    os.listdir(os.path.join(triage_by_casr, "reports_dedup"))
                )
            if os.path.exists(os.path.join(triage_by_casr, "reports_dedup_cluster")):
                triage["casr_dedup_cluster"] = len(
                    os.listdir(os.path.join(triage_by_casr, "reports_dedup_cluster"))
                )
            summary_by_unique_line_path = os.path.join(
                triage_by_casr, "summary_by_unique_line"
            )
            if os.path.isfile(summary_by_unique_line_path):
                with open(summary_by_unique_line_path) as f:
                    summary_content = f.read()
                data_str = summary_content.split("->")[-1]
                pattern = r"(.+?): (\d+)"
                for match in re.findall(pattern, data_str):
                    key, value = match
                    key = key.strip()
                    value = int(value.strip())
                    triage[key] = value
                    triage["unique_line"] += value
            triage_results.setdefault(target, []).append(triage)
        for target in triage_results.keys():
            triage_results[target] = sorted(
                triage_results[target],
                key=lambda x: (
                    x["unique_line"],
                    x["casr_dedup_cluster"],
                    x["casr_dedup"],
                ),
                reverse=True,
            )
        utility.console.print(f"The results can be found in {WORK_DIR_TRIAGE_BY_CASR}")
        return triage_results

    @staticmethod
    def sort_by_severity(field):
        if field in CasrTriageAnalysis.Severity["EXPLOITABLE"]:
            return 0, field
        elif field in CasrTriageAnalysis.Severity["PROBABLY_EXPLOITABLE"]:
            return 1, field
        return 2, field

    @staticmethod
    def get_severity_color(field):
        color = "000000"
        if field in CasrTriageAnalysis.Severity["EXPLOITABLE"]:
            color = "800000"
        elif field in CasrTriageAnalysis.Severity["PROBABLY_EXPLOITABLE"]:
            color = "1F497D"
        return color

    @staticmethod
    # @utility.time_count("SAVE TRIAGE BY CASR@https://github.com/ispras/casr DONE!")
    def save_triage_by_casr_results(
        WORK_DIR, OUTPUT_FILE=None, MEMORY_RELATED_BUGS_FIELD=False
    ):
        if OUTPUT_FILE is None:
            OUTPUT_FILE = os.path.join(
                os.path.dirname(WORK_DIR),
                f"{os.path.basename(WORK_DIR)}_triage_by_casr.xlsx",
            )
        triage_results = CasrTriageAnalysis.triage_by_casr(WORK_DIR)
        excel_manager = ExcelManager()
        for target in sorted(triage_results.keys()):
            table_data = triage_results[target]
            bug_fields = list(set([_ for item in table_data for _ in item.keys()]))
            bug_fields = [
                item
                for item in bug_fields
                if item not in CasrTriageAnalysis.display_fields
            ]
            bug_fields = sorted(bug_fields, key=CasrTriageAnalysis.sort_by_severity)
            if MEMORY_RELATED_BUGS_FIELD:
                display_fields = (
                    CasrTriageAnalysis.display_fields
                    + [MEMORY_RELATED_BUGS]
                    + bug_fields
                )
            else:
                display_fields = CasrTriageAnalysis.display_fields + bug_fields
            excel_manager.create_sheet(target)
            # the header of table
            excel_manager.set_sheet_header(
                display_fields,
                [
                    {
                        "Font": Font(
                            bold=True,
                            name="Calibri",
                            size=17,
                            color=CasrTriageAnalysis.get_severity_color(display_field),
                        )
                    }
                    for display_field in display_fields
                ],
            )
            # the rows of table
            for item in table_data:
                if MEMORY_RELATED_BUGS_FIELD:
                    item[MEMORY_RELATED_BUGS] = 0
                    for bug_field in bug_fields:
                        if (
                            bug_field in item.keys()
                            and CasrTriageAnalysis.is_memory_related_bug(bug_field)
                        ):
                            item[MEMORY_RELATED_BUGS] += item[bug_field]
                excel_manager.set_sheet_data(
                    [
                        item[display_field] if display_field in item.keys() else ""
                        for display_field in display_fields
                    ],
                    [
                        {
                            "Fill": PatternFill(
                                fgColor=CasrTriageAnalysis.fuzzer_colors[
                                    item["fuzzer"]
                                ],
                                fill_type="solid",
                            )
                        }
                        if item["fuzzer"] in CasrTriageAnalysis.fuzzer_colors.keys()
                        else {}
                        for _ in display_fields
                    ],
                )
        excel_manager.save_workbook(OUTPUT_FILE)
        utility.console.print(
            f"triage by casr@https://github.com/ispras/casr are saved in {OUTPUT_FILE}"
        )
        return OUTPUT_FILE

    @staticmethod
    # @utility.time_count("BUG FOUND BY TIME DONE!")
    def get_bug_found_by_speed(WORK_DIR):
        assert os.path.exists(WORK_DIR), f"{WORK_DIR} not exists"
        bug_info = {}
        for summary_path in utility.summary_paths(WORK_DIR):
            fuzzer, target, repeat = utility.parse_path_by(summary_path)
            with open(summary_path, "r") as f:
                lines = f.readlines()
                for i in range(len(lines)):
                    if "Crash: " in lines[i]:
                        time = ""
                        execs = ""
                        bug_type = ""
                        crash_line = ""
                        crash_file_name = lines[i].lstrip("Crash: ").strip()
                        for item in crash_file_name.split(","):
                            if item.startswith("time:"):
                                time = item.lstrip("time:").strip()
                            elif item.startswith("execs:"):
                                execs = item.lstrip("execs:").strip()
                        casrep_split = lines[i + 1].split(":")
                        bug_type = casrep_split[2].strip()
                        crash_line = ":".join(casrep_split[3:]).strip()
                        crash_line = crash_line.split("/")[-1]
                        bug_info.setdefault(target, []).append(
                            {
                                "fuzzer": fuzzer,
                                "repeat": repeat,
                                "time": utility.get_readable_time(
                                    round(int(time) / 1000)
                                )
                                if time.isnumeric()
                                else "unknown",
                                "execs": execs if len(execs) > 0 else "unknown",
                                "bug_type": bug_type,
                                "crash_line": crash_line,
                            }
                        )
        return bug_info

    @staticmethod
    # @utility.time_count("SAVE BUG FOUND BY SPEED DONE!")
    def save_bug_found_by_speed(WORK_DIR, OUTPUT_FILE=None):
        bug_info = CasrTriageAnalysis.get_bug_found_by_speed(WORK_DIR)
        if OUTPUT_FILE is None:
            OUTPUT_FILE = os.path.join(
                os.path.dirname(WORK_DIR),
                f"{os.path.basename(WORK_DIR)}_bug_found_by_speed.xlsx",
            )
        excel_manager = ExcelManager()
        for target in sorted(bug_info.keys()):
            table_data = bug_info[target]
            field_order = list(set([item["bug_type"] for item in table_data]))
            field_order = sorted(field_order, key=CasrTriageAnalysis.sort_by_severity)
            bug_fields = {}
            for item in table_data:
                bug_fields.setdefault(item["bug_type"], []).append(item["crash_line"])
            for key in bug_fields.keys():
                bug_fields[key] = sorted(list(set(bug_fields[key])))
            bug_fields = [
                bug_type + "/" + crash_line
                for bug_type in field_order
                for crash_line in bug_fields[bug_type]
            ]
            display_fields = [
                "fuzzer",
                "repeat",
            ] + bug_fields
            excel_manager.create_sheet(target)
            # the header of table
            excel_manager.set_sheet_header(
                display_fields + ["SUM"],
                [
                    {
                        "Font": Font(
                            bold=True,
                            name="Calibri",
                            size=17,
                            color=CasrTriageAnalysis.get_severity_color(
                                display_field.split("/")[0].strip()
                            ),
                        )
                    }
                    for display_field in display_fields
                ]
                + [
                    {
                        "Font": Font(
                            bold=True,
                            name="Calibri",
                            size=17,
                        )
                    }
                ],
                direction="vertical",
            )
            tmp_data = {}
            for item in table_data:
                tmp_data.setdefault(item["fuzzer"], {}).setdefault(item["repeat"], {})[
                    item["bug_type"] + "/" + item["crash_line"]
                ] = (item["time"] + " / " + item["execs"])
            table_data = [
                {"fuzzer": fuzzer, "repeat": repeat, **tmp_data[fuzzer][repeat]}
                for fuzzer in tmp_data
                for repeat in tmp_data[fuzzer]
            ]
            table_data = sorted(
                table_data,
                key=lambda x: (
                    len(x) - 2,
                    x["fuzzer"],
                    x["repeat"],
                ),
                reverse=True,
            )
            # the rows of table
            for item in table_data:
                excel_manager.set_sheet_data(
                    [
                        item[display_field] if display_field in item.keys() else ""
                        for display_field in display_fields
                    ]
                    + [len(item) - 2],
                    [
                        {
                            "Fill": PatternFill(
                                fgColor=CasrTriageAnalysis.fuzzer_colors[
                                    item["fuzzer"]
                                ],
                                fill_type="solid",
                            )
                        }
                        if item["fuzzer"] in CasrTriageAnalysis.fuzzer_colors.keys()
                        else {}
                        for _ in display_fields
                    ]
                    + [{}],
                    direction="vertical",
                )
        excel_manager.save_workbook(OUTPUT_FILE)
        utility.console.print(f"Bug found by time are saved in {OUTPUT_FILE}")
        return OUTPUT_FILE
