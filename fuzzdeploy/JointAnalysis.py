import copy
import os

import openpyxl

from . import utility


class JointAnalysis:
    @staticmethod
    def copy_cell(source_cell, target_cell):
        target_cell.value = copy.copy(source_cell.value)
        target_cell._style = copy.copy(source_cell._style)
        target_cell.font = copy.copy(source_cell.font)
        target_cell.alignment = copy.copy(source_cell.alignment)
        target_cell.border = copy.copy(source_cell.border)
        target_cell.fill = copy.copy(source_cell.fill)
        target_cell.number_format = copy.copy(source_cell.number_format)
        target_cell.protection = copy.copy(source_cell.protection)

    @staticmethod
    @utility.time_count("MERGE FILES DONE!")
    def save_state_results(STATS_FILE, TRIAGE_FILE, OUTPUT_FILE):
        assert os.path.exists(STATS_FILE), f"{STATS_FILE} not found"
        assert os.path.exists(TRIAGE_FILE), f"{TRIAGE_FILE} not found"
        assert OUTPUT_FILE is not None, f"{OUTPUT_FILE} is None"
        stats_wb = openpyxl.load_workbook(STATS_FILE)
        triage_wb = openpyxl.load_workbook(TRIAGE_FILE)
        wb = openpyxl.Workbook()
        wb.remove(wb["Sheet"])
        for triage_sheet in triage_wb.worksheets:
            sheet_name = triage_sheet.title
            assert (
                sheet_name in stats_wb.sheetnames
            ), f"{sheet_name} not found in {TRIAGE_FILE}. Is it generated from the same workdir?"
            stats_sheet = stats_wb[sheet_name]
            output_sheet = wb.create_sheet(sheet_name)

            display_fields = list(triage_sheet[1])
            fuzzer_fields = list(stats_sheet[1])
            display_fields += [
                field
                for field in fuzzer_fields
                if field.value not in [_.value for _ in display_fields]
            ]
            for col_idx, display_field in enumerate(display_fields, start=1):
                JointAnalysis.copy_cell(
                    display_field,
                    output_sheet.cell(row=1, column=col_idx),
                )
            for triage_row in triage_sheet.iter_rows(min_row=2):
                fuzzer = triage_row[0].value
                repeat = triage_row[1].value
                for stats_row in stats_sheet.iter_rows(min_row=2):
                    if stats_row[0].value == fuzzer and stats_row[1].value == repeat:
                        for col_idx, cell in enumerate(
                            [cell for cell in triage_row] + list(stats_row[2:]), start=1
                        ):
                            JointAnalysis.copy_cell(
                                cell,
                                output_sheet.cell(
                                    row=triage_row[0].row, column=col_idx
                                ),
                            )
                        break
            # auto adjust width
            for col in output_sheet.columns:
                max_length = 0
                for cell in col:
                    try:
                        cell_len = utility.realLength(str(cell.value))[2]
                        if cell_len > max_length:
                            max_length = cell_len
                    except:
                        pass
                output_sheet.column_dimensions[col[0].column_letter].width = (
                    max_length * 1.7
                )
        wb.save(OUTPUT_FILE)
        utility.console.print(f"The merged result can be found in {OUTPUT_FILE}")
        return OUTPUT_FILE
