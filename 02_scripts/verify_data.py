# -*- coding: utf-8 -*-
"""
verify_data.py
==============
Data Quality/Sanity Check untuk dataset hasil cleaning.

Cara pakai:
    python verify_data.py
"""

from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "../03_clean_data"

ASEAN_FILE = OUTPUT_DIR / "dataset_asia_tenggara_clean.csv"
INDONESIA_FILE = OUTPUT_DIR / "dataset_indonesia_clean.csv"

FILTER_COLUMNS = [
    "jenis_disagregasi_1",
    "kategori_disagregasi_1",
    "jenis_disagregasi_2",
    "kategori_disagregasi_2",
]

DUPLICATE_KEY = [
    "kode_wilayah",
    "tahun",
    "id_indikator_unik",
    "jenis_disagregasi_1",
    "kategori_disagregasi_1",
    "jenis_disagregasi_2",
    "kategori_disagregasi_2",
]

ALLOWED_REGIONS = {"Jawa", "Luar Jawa"}
ALLOWED_ASEAN_COUNTRIES = {
    "Brunei Darussalam",
    "Indonesia",
    "Cambodia",
    "Laos",
    "Myanmar",
    "Malaysia",
    "Philippines",
    "Singapore",
    "Thailand",
    "Timor-Leste",
    "Viet Nam",
}


def load_csv(path: Path) -> pd.DataFrame:
    """Load a cleaned CSV using the same BOM-safe encoding as clean_data.py."""
    if not path.exists():
        raise FileNotFoundError(f"File output tidak ditemukan: {path}")
    return pd.read_csv(path, encoding="utf-8-sig")


def assert_columns_exist(df: pd.DataFrame, columns: list[str], dataset_name: str) -> None:
    missing_columns = [column for column in columns if column not in df.columns]
    assert not missing_columns, (
        f"{dataset_name}: kolom wajib tidak ditemukan: {missing_columns}"
    )


def check_filter_columns(df: pd.DataFrame, dataset_name: str) -> None:
    null_counts = df[FILTER_COLUMNS].isna().sum()
    invalid_columns = null_counts[null_counts > 0].to_dict()
    assert not invalid_columns, (
        f"{dataset_name}: ditemukan NaN/None pada kolom filter: {invalid_columns}"
    )
    print(f"[PASS] {dataset_name}: kolom filter tidak memiliki NaN/None")


def check_duplicates(df: pd.DataFrame, dataset_name: str) -> None:
    duplicate_count = int(df.duplicated(subset=DUPLICATE_KEY).sum())
    assert duplicate_count == 0, (
        f"{dataset_name}: ditemukan {duplicate_count} baris duplikat "
        f"berdasarkan key {DUPLICATE_KEY}"
    )
    print(f"[PASS] {dataset_name}: tidak ada duplikasi berdasarkan key")


def check_allowed_values(
    df: pd.DataFrame,
    column: str,
    allowed_values: set[str],
    dataset_name: str,
) -> None:
    actual_values = set(df[column].dropna().unique())
    invalid_values = actual_values - allowed_values
    missing_values = df[column].isna().sum()
    if invalid_values or missing_values > 0:
        print(
            f"[WARNING] {dataset_name}: nilai tidak sesuai pada '{column}': "
            f"{sorted(invalid_values)}, null/kosong: {missing_values}"
        )
        return
    print(f"[PASS] {dataset_name}: nilai '{column}' sesuai daftar yang diizinkan")


def main() -> None:
    df_asean = load_csv(ASEAN_FILE)
    df_indonesia = load_csv(INDONESIA_FILE)

    assert_columns_exist(
        df_asean,
        [*FILTER_COLUMNS, *DUPLICATE_KEY, "nama_wilayah"],
        "Dataset ASEAN",
    )
    assert_columns_exist(
        df_indonesia,
        [*FILTER_COLUMNS, *DUPLICATE_KEY, "region_group"],
        "Dataset Indonesia",
    )

    check_filter_columns(df_asean, "Dataset ASEAN")
    check_filter_columns(df_indonesia, "Dataset Indonesia")

    check_duplicates(df_asean, "Dataset ASEAN")
    check_duplicates(df_indonesia, "Dataset Indonesia")

    check_allowed_values(
        df_indonesia,
        "region_group",
        ALLOWED_REGIONS,
        "Dataset Indonesia",
    )
    check_allowed_values(
        df_asean,
        "nama_wilayah",
        ALLOWED_ASEAN_COUNTRIES,
        "Dataset ASEAN",
    )

    print("\nPemeriksaan data selesai.")


if __name__ == "__main__":
    main()
