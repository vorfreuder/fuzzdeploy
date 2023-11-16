import json
import os
import re

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill

from . import utility
from .Builder import Builder


class CasrTriageAnalysis:
    fuzzer_colors = {
        "aflplusplus": "00A0B0",
        "htfuzz": "FBD26A",
        # "ctxhtfuzz": "D8E4BC",
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
    @utility.time_count("CRASH TRIAGE BY CASR@https://github.com/ispras/casr DONE!")
    def triage_by_casr(WORK_DIR):
        assert os.path.exists(WORK_DIR), f"{WORK_DIR} not exists"
        WORK_DIR_TRIAGE_BY_CASR = os.path.join(WORK_DIR, "triage_by_casr")
        # check if images exist
        FUZZERS = set()
        TARGETS = set()
        for test_path in utility.test_paths(WORK_DIR):
            fuzzer, target, repeat = utility.parse_path_by(test_path)
            FUZZERS.add(fuzzer)
            TARGETS.add(target)
        Builder.build_imgs(FUZZERS=list(FUZZERS), TARGETS=list(TARGETS))
        container_id_ls = []
        cpu_id_range = []
        triage_by_casr_ls = []
        with utility.console.status(
            "[bold green]Triaging",
            spinner="arrow3",
        ) as status:
            for test_path in utility.test_paths(WORK_DIR):
                assert os.path.exists(
                    os.path.join(test_path, "target_args")
                ), f"target_args not found in {test_path}"
                fuzzer_stats_path = utility.search_file(test_path, "fuzzer_stats")
                if fuzzer_stats_path is None:
                    utility.console.print(
                        f"[yellow]Warning: fuzzer_stats not found in {test_path}, maybe fine.[/yellow]"
                    )
                fuzzer, target, repeat = utility.parse_path_by(test_path)
                if len(cpu_id_range) == 0:
                    status.update(f"[bold green]Waiting for free cpu")
                    cpu_id_range = utility.get_free_cpu_range()
                    status.update("[bold green]Triaging")
                triage_by_casr = os.path.join(
                    WORK_DIR_TRIAGE_BY_CASR, fuzzer, target, repeat
                )
                os.makedirs(triage_by_casr, exist_ok=True)
                triage_by_casr_ls.append(triage_by_casr)
                # try:
                #     with open(
                #         os.path.join(triage_by_casr, "summary_by_unique_line")
                #     ) as f:
                #         if len(f.read().strip()) > 0:
                #             utility.console.print(
                #                 f"{triage_by_casr} already triaged, skip it"
                #             )
                #             continue
                # except:
                #     pass
                container_id = utility.get_cmd_res(
                    f"""
            docker run \
            -itd \
            --rm \
            --volume={test_path}:/shared \
            --volume={triage_by_casr}:/triage_by_casr \
            --cap-add=SYS_PTRACE \
            --security-opt seccomp=unconfined \
            --cpuset-cpus="{cpu_id_range.pop(0)}" \
            --network=none \
            "{fuzzer}/{target}" \
            -c '${{SRC}}/triage_by_casr.sh'
                    """
                ).strip()
                container_id_ls.append(container_id)
            for container_id in container_id_ls:
                utility.get_cmd_res(f"docker wait {container_id} 2> /dev/null")
        triage_results = {}
        for triage_by_casr in triage_by_casr_ls:
            fuzzer, target, repeat = utility.parse_path_by(triage_by_casr)
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
    @utility.time_count("SAVE TRIAGE BY CASR@https://github.com/ispras/casr DONE!")
    def save_triage_by_casr_results(WORK_DIR, OUTPUT_FILE=None):
        triage_results = CasrTriageAnalysis.triage_by_casr(WORK_DIR)
        if OUTPUT_FILE is None:
            OUTPUT_FILE = os.path.join(
                os.path.dirname(WORK_DIR),
                f"{os.path.basename(WORK_DIR)}_triage_by_casr.xlsx",
            )
        wb = openpyxl.Workbook()
        wb.remove(wb["Sheet"])
        for target in sorted(triage_results.keys()):
            table_data = triage_results[target]
            bug_fields = list(set([_ for item in table_data for _ in item.keys()]))
            bug_fields = [
                item
                for item in bug_fields
                if item not in CasrTriageAnalysis.display_fields
            ]
            bug_fields = sorted(bug_fields, key=CasrTriageAnalysis.sort_by_severity)
            display_fields = CasrTriageAnalysis.display_fields + bug_fields
            ws = wb.create_sheet(target)
            # the header of table
            for col_idx, display_field in enumerate(display_fields, start=1):
                ws.cell(row=1, column=col_idx, value=display_field)
                ws.cell(row=1, column=col_idx).font = Font(
                    bold=True,
                    name="Calibri",
                    size=17,
                    color=CasrTriageAnalysis.get_severity_color(display_field),
                )
                ws.cell(row=1, column=col_idx).alignment = Alignment(
                    horizontal="center", vertical="center"
                )
            # the rows of table
            for row_idx, data in enumerate(table_data, start=2):
                for col_idx, display_field in enumerate(display_fields, start=1):
                    ws.cell(
                        row=row_idx,
                        column=col_idx,
                        value=data[display_field]
                        if display_field in data.keys()
                        else "",
                    )
                    ws.cell(row=row_idx, column=col_idx).font = Font(
                        name="Calibri", size=17
                    )
                    ws.cell(row=row_idx, column=col_idx).alignment = Alignment(
                        horizontal="center", vertical="center"
                    )
            # auto adjust width
            for col in ws.columns:
                max_length = 0
                for cell in col:
                    try:
                        cell_len = utility.realLength(str(cell.value))[2]
                        if cell_len > max_length:
                            max_length = cell_len
                    except:
                        pass
                ws.column_dimensions[col[0].column_letter].width = max_length * 1.7
            # row paint
            for row in ws.iter_rows(min_row=2):
                fuzzer = row[0].value
                for fuzzer_name, color in CasrTriageAnalysis.fuzzer_colors.items():
                    if fuzzer.startswith(fuzzer_name):
                        for cell in row:
                            cell.fill = PatternFill(
                                fgColor=color,
                                fill_type="solid",
                            )
                        break
        wb.save(OUTPUT_FILE)
        utility.console.print(
            f"triage by casr@https://github.com/ispras/casr are saved in {OUTPUT_FILE}"
        )
        return OUTPUT_FILE

    @staticmethod
    @utility.time_count("BUG FOUND BY TIME DONE!")
    def bug_found_by_speed(WORK_DIR):
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
    @utility.time_count("SAVE BUG FOUND BY TIME DONE!")
    def save_bug_found_by_speed(WORK_DIR, OUTPUT_FILE=None):
        bug_info = CasrTriageAnalysis.bug_found_by_speed(WORK_DIR)
        if OUTPUT_FILE is None:
            OUTPUT_FILE = os.path.join(
                os.path.dirname(WORK_DIR),
                f"{os.path.basename(WORK_DIR)}_bug_found_by_time.xlsx",
            )
        wb = openpyxl.Workbook()
        wb.remove(wb["Sheet"])
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
            ws = wb.create_sheet(target)
            # the header of table
            for row_idx, display_field in enumerate(display_fields, start=1):
                ws.cell(row=row_idx, column=1, value=display_field)
                ws.cell(row=row_idx, column=1).font = Font(
                    bold=True,
                    name="Calibri",
                    size=17,
                    color=CasrTriageAnalysis.get_severity_color(
                        display_field.split("/")[0]
                    ),
                )
                ws.cell(row=row_idx, column=1).alignment = Alignment(
                    horizontal="center", vertical="center"
                )
            ws.cell(row=len(display_fields) + 1, column=1, value="SUM")
            ws.cell(row=len(display_fields) + 1, column=1).font = Font(
                bold=True,
                name="Calibri",
                size=17,
                color=CasrTriageAnalysis.get_severity_color(
                    display_field.split("/")[0]
                ),
            )
            ws.cell(row=len(display_fields) + 1, column=1).alignment = Alignment(
                horizontal="center", vertical="center"
            )
            tmp_data = {}
            for item in table_data:
                tmp_data.setdefault(item["fuzzer"], {}).setdefault(item["repeat"], {})[
                    item["bug_type"] + "/" + item["crash_line"]
                ] = (item["time"] + " \ " + item["execs"])
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
            for col_idx, data in enumerate(table_data, start=2):
                for row_idx, display_field in enumerate(display_fields, start=1):
                    ws.cell(
                        row=row_idx,
                        column=col_idx,
                        value=data[display_field]
                        if display_field in data.keys()
                        else "",
                    )
                    ws.cell(row=row_idx, column=col_idx).font = Font(
                        name="Calibri", size=17
                    )
                    ws.cell(row=row_idx, column=col_idx).alignment = Alignment(
                        horizontal="center", vertical="center"
                    )
                ws.cell(
                    row=len(display_fields) + 1,
                    column=col_idx,
                    value=len(data) - 2,
                )
                ws.cell(
                    row=len(display_fields) + 1,
                    column=col_idx,
                ).font = Font(name="Calibri", size=17)
                ws.cell(
                    row=len(display_fields) + 1,
                    column=col_idx,
                ).alignment = Alignment(horizontal="center", vertical="center")
            # auto adjust width
            for col in ws.columns:
                max_length = 0
                for cell in col:
                    try:
                        cell_len = utility.realLength(str(cell.value))[2]
                        if cell_len > max_length:
                            max_length = cell_len
                    except:
                        pass
                ws.column_dimensions[col[0].column_letter].width = max_length * 1.7
            # column paint
            for row in ws.iter_rows(min_row=1, max_row=1):
                for cell in row:
                    fuzzer = cell.value
                    for fuzzer_name, color in CasrTriageAnalysis.fuzzer_colors.items():
                        if fuzzer.startswith(fuzzer_name):
                            for idx in range(1, ws.max_row + 1):
                                ws.cell(row=idx, column=cell.column).fill = PatternFill(
                                    fgColor=color,
                                    fill_type="solid",
                                )
                            break
        wb.save(OUTPUT_FILE)
        utility.console.print(
            f"triage by casr@https://github.com/ispras/casr are saved in {OUTPUT_FILE}"
        )
        return OUTPUT_FILE
