import os

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill

from . import utility


class StateAnalysis:
    fuzzer_colors = {
        "aflplusplus": "00A0B0",
        "htfuzz": "FBD26A",
    }
    display_fields = [
        "fuzzer",
        "repeat",
        "crashes",  # AFL++ not support
        "pending_favs",
        "execs_done",
        "bitmap_cvg",
        "execute_time",
        "execs_per_sec",
        "unique_hangs",  # AFL++ not support
        "pending_total",
        "execs_since_crash",
    ]

    @staticmethod
    @utility.time_count("COLLECT FUZZER_STATS DONE!")
    def get_state_results(WORK_DIR):
        assert os.path.exists(WORK_DIR), f"{WORK_DIR} not exists"
        no_fuzzer_stats_ls = []
        state_results = {}
        for test_path in utility.test_paths(WORK_DIR):
            fuzzer, target, repeat = utility.parse_path_by(test_path)
            fuzzer_stats_path = utility.search_file(test_path, "fuzzer_stats")
            if fuzzer_stats_path is None:
                no_fuzzer_stats_ls.append(f"{fuzzer}/{target}/{repeat}")
                continue
            state = {"fuzzer": fuzzer, "repeat": repeat}
            with open(fuzzer_stats_path, "r") as f:
                fuzzer_stats = f.read()
            for item in fuzzer_stats.strip().split("\n"):
                l, r = item.split(":")
                state[l.strip()] = r.strip()
            div = (int(state["last_update"]) - int(state["start_time"])) / 3600
            state["execute_time"] = f"{div:.5f}"
            state["crashes"] = (
                int(state["unique_crashes"])
                if state.get("unique_crashes")
                else int(state["saved_crashes"])
            )
            state["unique_hangs"] = (
                int(state["unique_hangs"])
                if state.get("unique_hangs")
                else int(state["saved_hangs"])
            )
            state_results.setdefault(target, []).append(state)
        for target in state_results.keys():
            state_results[target] = sorted(
                state_results[target],
                key=lambda x: int(x["crashes"]) / float(x["execute_time"]),
                reverse=True,
            )
        assert (
            len(state_results) > 0
        ), "No fuzzer_stats found! Is fuzzer working correctly?"
        if len(no_fuzzer_stats_ls) > 0:
            utility.console.print(
                f"[yellow]Warning: {len(no_fuzzer_stats_ls)} fuzzer_stats not found:[/yellow]",
                end=" ",
            )
            for item in no_fuzzer_stats_ls:
                print(f"{item}", end=" ")
            utility.console.print(f"[yellow]and ignored in output file![/yellow]")
        return state_results

    @staticmethod
    @utility.time_count("SAVE FUZZER_STATS DONE!")
    def save_state_results(WORK_DIR, OUTPUT_FILE=None):
        state_results = StateAnalysis.get_state_results(WORK_DIR)
        if OUTPUT_FILE is None:
            OUTPUT_FILE = os.path.join(
                os.path.dirname(WORK_DIR),
                f"{os.path.basename(WORK_DIR)}_fuzzer_stats.xlsx",
            )
        wb = openpyxl.Workbook()
        wb.remove(wb["Sheet"])
        display_fields = StateAnalysis.display_fields
        for target in sorted(state_results.keys()):
            table_data = state_results[target]
            ws = wb.create_sheet(target)
            # the header of table
            for col_idx, display_field in enumerate(display_fields, start=1):
                ws.cell(row=1, column=col_idx, value=display_field)
                ws.cell(row=1, column=col_idx).font = Font(
                    bold=True,
                    name="Calibri",
                    size=17,
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
                for fuzzer_name, color in StateAnalysis.fuzzer_colors.items():
                    if fuzzer.startswith(fuzzer_name):
                        for cell in row:
                            cell.fill = PatternFill(
                                fgColor=color,
                                fill_type="solid",
                            )
                        break
        wb.save(OUTPUT_FILE)
        utility.console.print(f"The result can be found in {OUTPUT_FILE}")
        return OUTPUT_FILE
