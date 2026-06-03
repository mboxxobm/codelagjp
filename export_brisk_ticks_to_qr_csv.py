#!/usr/bin/env python3
"""
Export BRISK/BRISX multi-symbol tick JSON into per-symbol qr-*.csv files.

Input:
  main_Ticks.json   {"map": {"p":"price", "t":"timestamp", ...}, "ticks": {"6501": [...]}}
  main_Masters.json {"6501": {"timestamp": epoch_microseconds, ...}, ...}

Output format:
  値段,株数,金額,時刻
  5066,100,506600,14:45:39

Rows are written newest first to match existing qr-*.csv files.
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any


JST = timezone(timedelta(hours=9))
CSV_HEADER = ["値段", "株数", "金額", "時刻"]


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def value(row: dict[str, Any], field_map: dict[str, str], name: str) -> Any:
    if name in row:
        return row[name]
    for short_key, long_name in field_map.items():
        if long_name == name and short_key in row:
            return row[short_key]
    return None


def jst_date_from_masters(masters: dict[str, Any]) -> str:
    for master in masters.values():
        ts = master.get("timestamp") if isinstance(master, dict) else None
        if ts:
            return datetime.fromtimestamp(int(ts) / 1_000_000, JST).strftime("%Y%m%d")
    raise ValueError("main_Masters.json から取引日を判定できませんでした")


def format_price(price: Any) -> str:
    d = Decimal(str(price))
    if d == d.to_integral_value():
        return str(int(d))
    return format(d.normalize(), "f")


def format_amount(price: Any, quantity: Any) -> str:
    amount = Decimal(str(price)) * Decimal(str(quantity))
    rounded = amount.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return str(int(rounded))


def format_time_from_day_microseconds(raw_timestamp: Any) -> str:
    n = int(raw_timestamp)
    if n > 1_000_000_000_000_000:
        dt = datetime.fromtimestamp(n / 1_000_000, JST)
        return dt.strftime("%H:%M:%S")
    if n > 1_000_000_000_000:
        dt = datetime.fromtimestamp(n / 1000, JST)
        return dt.strftime("%H:%M:%S")
    if n > 1_000_000_000:
        seconds = n / 1_000_000
    elif n > 1_000_000:
        seconds = n / 1000
    else:
        seconds = n
    hh = int(seconds // 3600)
    mm = int((seconds % 3600) // 60)
    ss = int(seconds % 60)
    return f"{hh:02d}:{mm:02d}:{ss:02d}"


def export_symbol(
    code: str,
    rows: list[dict[str, Any]],
    field_map: dict[str, str],
    out_path: Path,
) -> int:
    normalized = []
    for i, row in enumerate(rows):
        price = value(row, field_map, "price")
        quantity = value(row, field_map, "quantity")
        timestamp = value(row, field_map, "timestamp")
        frame = value(row, field_map, "frame") or 0
        if price is None or quantity is None or timestamp is None:
            continue
        normalized.append((int(timestamp), int(frame), i, price, int(quantity)))

    normalized.sort(key=lambda x: (x[0], x[1], x[2]), reverse=True)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f, lineterminator="\r\n")
        writer.writerow(CSV_HEADER)
        for timestamp, _frame, _index, price, quantity in normalized:
            writer.writerow([
                format_price(price),
                quantity,
                format_amount(price, quantity),
                format_time_from_day_microseconds(timestamp),
            ])
    return len(normalized)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--code", action="append", help="Export only this code. Can be repeated.")
    args = parser.parse_args()

    ticks_root = load_json(args.input_dir / "main_Ticks.json")
    masters = load_json(args.input_dir / "main_Masters.json")
    field_map = ticks_root.get("map", {})
    ticks = ticks_root.get("ticks", {})
    if not isinstance(ticks, dict):
        raise ValueError("main_Ticks.json に ticks オブジェクトがありません")

    trade_date = jst_date_from_masters(masters)
    requested = set(args.code or ticks.keys())

    exported = []
    for code in sorted(requested):
        rows = ticks.get(code)
        if not rows:
            print(f"skip {code}: ticks not found")
            continue
        out_path = args.output_dir / f"qr-{code}-{trade_date}.csv"
        count = export_symbol(code, rows, field_map, out_path)
        exported.append((code, count, out_path))
        print(f"wrote {out_path} ({count:,} rows)")

    print(f"exported {len(exported)} files for {trade_date}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
