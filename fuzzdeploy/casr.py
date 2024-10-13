import datetime
import multiprocessing
import re
import time
from pathlib import Path

import pandas as pd
from styleframe import StyleFrame, Styler, utils

from .make import make
from .utils import WorkDirItem, get_item_path, work_dir_iterdir


def _skip_handler(item: WorkDirItem) -> bool:
    dst_path = item.work_dir / "casr" / item.fuzzer / item.target / item.idx
    if not dst_path.exists():
        return False
    crash_set = set(
        [p.name for p in item.path.glob("*") if p.is_file() and p.name.startswith("id")]
    )
    if len(crash_set) == 0 and not (dst_path / "summary_by_unique_line").exists():
        return False
    failed_path = dst_path / "failed"
    if failed_path.exists():
        for p in failed_path.glob("*"):
            if p.name in crash_set:
                crash_set.remove(p.name)
    reports_path = dst_path / "reports"
    if reports_path.exists():
        for p in reports_path.glob("*"):
            if not p.name.endswith(".casrep"):
                continue
            file_name = p.name.rstrip(".casrep")
            if file_name in crash_set:
                crash_set.remove(file_name)
    return len(crash_set) == 0


def _print_progress(work_dir: str | Path):
    current_time = datetime.datetime.now()
    work_dir = Path(work_dir).absolute()
    untriaged = {}
    total_number = 0
    for item in work_dir_iterdir(work_dir, "archive"):
        key = (item.fuzzer, item.target, item.idx)
        untriaged[key] = set()
        crashes_path = get_item_path(item.path, "crashes")
        if not crashes_path:
            print(f"{item.path} crashes not found")
            continue
        for p in crashes_path.glob("*"):
            if p.name.startswith("id"):
                untriaged[key].add(p.name)
        total_number += len(untriaged[key])
    while True:
        if not (work_dir / "casr").exists():
            time.sleep(1)
            continue
        for item in work_dir_iterdir(work_dir, "casr"):
            dst_path = item.work_dir / "casr" / item.fuzzer / item.target / item.idx
            if not dst_path.exists():
                continue
            crash_set = untriaged[(item.fuzzer, item.target, item.idx)]
            failed_path = dst_path / "failed"
            if failed_path.exists():
                for p in failed_path.glob("*"):
                    if p.name in crash_set:
                        crash_set.remove(p.name)
            reports_path = dst_path / "reports"
            if reports_path.exists():
                for p in reports_path.glob("*"):
                    if not p.name.endswith(".casrep"):
                        continue
                    file_name = p.name.rstrip(".casrep")
                    if file_name in crash_set:
                        crash_set.remove(file_name)
        current_total = sum([len(crash_set) for crash_set in untriaged.values()])
        print(
            f"\rcost time: {(datetime.datetime.now()-current_time)} current progress: {total_number-current_total}/{total_number}",
            end="",
            flush=True,
        )
        time.sleep(1)


def get(work_dir: str | Path):
    work_dir = Path(work_dir).absolute()
    p = multiprocessing.Process(target=_print_progress, args=(work_dir,), daemon=True)
    p.start()
    make(
        work_dir=work_dir,
        sub_dir="casr",
        base_image="casr",
        skip_handler=_skip_handler,
    )
    p.terminate()
    print()
    casr_res_ls = []
    for item in work_dir_iterdir(work_dir, "casr"):
        dst_path = item.work_dir / "casr" / item.fuzzer / item.target / item.idx
        casr_res = {
            "fuzzer": item.fuzzer,
            "target": item.target,
            "idx": item.idx,
            "unique_line": 0,
            "casr_dedup": 0,
            "casr_dedup_cluster": 0,
        }
        reports_dedup_path = dst_path / "reports_dedup"
        if reports_dedup_path.exists():
            casr_res["casr_dedup"] = len(list(reports_dedup_path.glob("*")))
        reports_dedup_cluster_path = dst_path / "reports_dedup_cluster"
        if reports_dedup_cluster_path.exists():
            casr_res["casr_dedup_cluster"] = len(
                list(reports_dedup_cluster_path.glob("*"))
            )
        summary_by_unique_line_path = dst_path / "summary_by_unique_line"
        if summary_by_unique_line_path.exists():
            with open(summary_by_unique_line_path, "r") as f:
                summary_content = f.read()
            data_str = summary_content.split("->")[-1]
            pattern = r"(.+?): (\d+)"
            for match in re.findall(pattern, data_str):
                key, value = match
                key = key.strip()
                value = int(value.strip())
                casr_res[key] = value
                casr_res["unique_line"] += value
        casr_res_ls.append(casr_res)
    df = pd.DataFrame(casr_res_ls)
    df.fillna(0, inplace=True)
    return df


def to_excel(work_dir: str | Path):
    work_dir = Path(work_dir).absolute()
    df = get(work_dir)
    excel_path = work_dir / f"{work_dir.name}_casr.xlsx"
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        for target, group in df.groupby("target"):
            group.sort_values(
                ["unique_line", "casr_dedup_cluster", "casr_dedup"],
                ascending=[False, False, False],
                inplace=True,
            )
            default_style = Styler(
                font=utils.fonts.calibri,
                font_size=17,
                wrap_text=False,
            )
            sf = StyleFrame(obj=group, styler_obj=default_style)

            header_style = Styler(
                bold=True,
                font=utils.fonts.calibri,
                font_size=17,
                wrap_text=False,
            )
            sf.apply_headers_style(styler_obj=header_style)

            sf.to_excel(
                writer,
                sheet_name=str(target),
                best_fit=group.columns.tolist(),
                columns_to_hide=["target"],
                columns_and_rows_to_freeze="A2",
            )
    print(f"save casr to {excel_path}")
