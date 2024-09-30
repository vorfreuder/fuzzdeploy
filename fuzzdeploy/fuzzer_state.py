from pathlib import Path

import numpy as np
import pandas as pd
from styleframe import StyleFrame, Styler, utils

from .utils import get_item_path, work_dir_iterdir


def get(work_dir: str | Path):
    data = []
    work_dir = Path(work_dir).absolute()
    for item in work_dir_iterdir(work_dir, "archive"):
        fuzzer_status_path = get_item_path(item.path, "fuzzer_stats")
        if fuzzer_status_path is None:
            print(f"{item.path}  fuzzer_stats not exists")
            continue
        content = fuzzer_status_path.open("r", encoding="utf-8").read()
        tmp = {}
        for line in content.strip().split("\n"):
            key, value = line.split(":", 1)
            tmp[key.strip()] = value.strip()
        tmp["fuzzer"] = item.fuzzer
        tmp["target"] = item.target
        tmp["idx"] = item.idx
        data.append(tmp)
    df = pd.DataFrame(data)

    def try_convert_to_numeric(column):
        converted = pd.to_numeric(column, errors="coerce")
        if converted.isna().any():
            return column
        return converted

    df = df.apply(try_convert_to_numeric)
    if not df.empty:
        df["idx"] = df["idx"].astype(str)
    return df


def to_excel(work_dir: str | Path):
    work_dir = Path(work_dir).absolute()
    df = get(work_dir)
    if df.empty:
        print("no fuzzer status data")
        return
    if "unique_crashes" not in df.columns:
        df["unique_crashes"] = np.nan
    if "saved_crashes" not in df.columns:
        df["saved_crashes"] = np.nan
    df["crashes"] = np.where(
        df["unique_crashes"].notna(), df["unique_crashes"], df["saved_crashes"]
    )
    if "unique_hangs" not in df.columns:
        df["unique_hangs"] = np.nan
    if "saved_hangs" not in df.columns:
        df["saved_hangs"] = np.nan
    df["unique_hangs"] = np.where(
        df["unique_hangs"].notna(), df["unique_hangs"], df["saved_hangs"]
    )
    df["execute_time"] = (df["last_update"] - df["start_time"]) / 3600
    df = df[
        [
            "fuzzer",
            "target",
            "idx",
            "crashes",
            "bitmap_cvg",
            "execs_done",
            "execute_time",
            "execs_per_sec",
            "unique_hangs",
            "pending_favs",
            "pending_total",
            "execs_since_crash",
        ]
    ]
    excel_path = work_dir / f"{work_dir.name}_fuzzer_status.xlsx"
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        for target, group in df.groupby("target"):
            group.sort_values(
                ["crashes", "execs_done"], ascending=[False, True], inplace=True
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
    print(f"save fuzzer status to {excel_path}")
