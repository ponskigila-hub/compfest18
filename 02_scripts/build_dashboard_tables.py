# -*- coding: utf-8 -*-
"""
build_dashboard_tables.py
==========================
Membuat 2 tabel siap-pakai untuk dashboard Power BI dari hasil clean_data.py:
  1. scatter_asean_gni_internet.csv  -> Halaman 1 (Macro: GNI vs Pengguna Internet ASEAN)
  2. gap_rural_urban_provinsi.csv    -> Halaman 2 & 3 (Micro/Policy: gap akses rural-urban)

Input  : ../03_clean_data/dataset_asia_tenggara_clean.csv
         ../03_clean_data/dataset_indonesia_clean.csv
Output : ../04_ready_for_dashboard/scatter_asean_gni_internet.csv
         ../04_ready_for_dashboard/gap_rural_urban_provinsi.csv

Cara pakai:
    cd 02_scripts
    python build_dashboard_tables.py
"""

import pandas as pd
from pathlib import Path

CLEAN_DIR = Path("../03_clean_data")
OUT_DIR = Path("../04_ready_for_dashboard")
OUT_DIR.mkdir(exist_ok=True)


# ============================================================
# TABEL 1: Scatter ASEAN — GNI per kapita x Pengguna Internet
# ============================================================
asean = pd.read_csv(CLEAN_DIR / "dataset_asia_tenggara_clean.csv")

gni = asean[asean["nama_indikator"] == "Pendapatan nasional bruto per kapita"][
    ["kode_wilayah", "nama_wilayah", "tahun", "nilai", "satuan"]
].rename(columns={"nilai": "gni_per_kapita_usd", "satuan": "satuan_gni"})

usr = asean[asean["nama_indikator"] == "Pengguna internet"][
    ["kode_wilayah", "nama_wilayah", "tahun", "nilai", "satuan"]
].rename(columns={"nilai": "pengguna_internet_persen", "satuan": "satuan_pengguna"})

scatter = pd.merge(gni, usr, on=["kode_wilayah", "nama_wilayah", "tahun"], how="outer")
scatter = scatter.sort_values(["nama_wilayah", "tahun"])

print("=== Tabel Scatter ASEAN ===")
print("Shape:", scatter.shape)
lengkap = scatter.dropna(subset=["gni_per_kapita_usd", "pengguna_internet_persen"]).shape[0]
print(f"Baris lengkap (punya GNI & pengguna internet): {lengkap} / {scatter.shape[0]}")
print("CATATAN: tahun 2025 & sebagian tahun Myanmar/Timor-Leste belum punya data")
print("pengguna internet -> jangan dipakai untuk scatter plot tanpa filter tahun.\n")

scatter.to_csv(OUT_DIR / "scatter_asean_gni_internet.csv", index=False, encoding="utf-8-sig")


# ============================================================
# TABEL 2: Gap Rural-Urban per Provinsi (Akses internet)
# ============================================================
idn = pd.read_csv(CLEAN_DIR / "dataset_indonesia_clean.csv")
akses = idn[idn["topik"] == "Akses internet"]

pivot = akses.pivot_table(
    index=["kode_wilayah", "nama_wilayah", "provinsi_induk_34", "region_group", "tahun"],
    columns="kategori_disagregasi_1",
    values="nilai",
).reset_index()
pivot.columns.name = None
pivot = pivot.rename(
    columns={
        "rural": "akses_rural_persen",
        "urban": "akses_urban_persen",
        "total": "akses_total_persen",
    }
)
pivot["gap_rural_urban_pp"] = pivot["akses_urban_persen"] - pivot["akses_rural_persen"]

print("=== Tabel Gap Rural-Urban ===")
print("Shape:", pivot.shape)
print("CATATAN: DKI Jakarta tidak punya nilai akses_rural_persen (wajar,")
print("provinsi ini 100% wilayah urban, bukan data hilang).\n")

pivot.to_csv(OUT_DIR / "gap_rural_urban_provinsi.csv", index=False, encoding="utf-8-sig")

print("Selesai. 2 file tersimpan di", OUT_DIR)


# ============================================================
# TABEL 3: Scatter DUNIA — GNI per kapita x Pengguna Internet
# (menggantikan/melengkapi scatter ASEAN, cakupan 201 negara)
# ============================================================
RAW_DIR = Path("../01_raw_data")
dunia = pd.read_csv(RAW_DIR / "dataset_dunia.csv")

# Normalisasi nama negara berdasarkan kode_wilayah (ISO3) — banyak negara
# punya 2 penulisan nama berbeda untuk kode yang sama (mis. "Lao P.D.R."
# vs "Lao PDR", "Turkiye" vs "Türkiye"). Pakai kode sebagai sumber kebenaran,
# sama seperti pendekatan normalisasi nama ASEAN sebelumnya.
canon_name = dunia.groupby("kode_wilayah")["nama_wilayah"].agg(lambda x: sorted(x.unique())[0])
n_sebelum = dunia["nama_wilayah"].nunique()
dunia["nama_wilayah"] = dunia["kode_wilayah"].map(canon_name)
n_sesudah = dunia["nama_wilayah"].nunique()
print(f"\n=== Tabel Scatter Dunia ===")
print(f"Normalisasi nama negara: {n_sebelum} -> {n_sesudah} nama unik")

gni_w = dunia[dunia["nama_indikator"] == "Pendapatan nasional bruto per kapita"][
    ["kode_wilayah", "nama_wilayah", "tahun", "nilai"]
].rename(columns={"nilai": "gni_per_kapita_usd"})

usr_w = dunia[dunia["nama_indikator"] == "Pengguna internet"][
    ["kode_wilayah", "nama_wilayah", "tahun", "nilai"]
].rename(columns={"nilai": "pengguna_internet_persen"})

scatter_w = pd.merge(gni_w, usr_w, on=["kode_wilayah", "nama_wilayah", "tahun"], how="inner")

ASEAN_CODES = {"BRN", "IDN", "KHM", "LAO", "MMR", "MYS", "PHL", "SGP", "THA", "TLS", "VNM"}
scatter_w["is_indonesia"] = scatter_w["kode_wilayah"] == "IDN"
scatter_w["is_asean"] = scatter_w["kode_wilayah"].isin(ASEAN_CODES)
scatter_w = scatter_w.sort_values(["tahun", "nama_wilayah"])

print("Shape:", scatter_w.shape, "| n negara:", scatter_w["nama_wilayah"].nunique())
print("CATATAN: tahun 2025 masih banyak bolong (baru 9 negara punya data")
print("pengguna internet) -> gunakan sampai 2024 untuk visual yang solid.")

scatter_w.to_csv(OUT_DIR / "scatter_dunia_gni_internet.csv", index=False, encoding="utf-8-sig")
print("Tersimpan:", OUT_DIR / "scatter_dunia_gni_internet.csv")


# ============================================================
# TABEL 4: Makro-Mikro Dunia — 6 faktor struktural per negara-tahun
# (untuk Halaman 1 Macro + Halaman 2 Mikro perbandingan head-to-head
#  Indonesia vs negara pembanding pilihan bebas)
# ============================================================
from functools import reduce

def ambil(df_src, nama_indikator, satuan_filter, kolom_baru):
    sub = df_src[df_src["nama_indikator"] == nama_indikator]
    if satuan_filter:
        sub = sub[sub["satuan"] == satuan_filter]
    return sub[["kode_wilayah", "nama_wilayah", "tahun", "nilai"]].rename(columns={"nilai": kolom_baru})

# pakai 'dunia' yang nama negaranya SUDAH dinormalisasi dari blok Tabel 3 di atas
internet_mm = ambil(dunia, "Pengguna internet", None, "pengguna_internet_persen")
gni_mm      = ambil(dunia, "Pendapatan nasional bruto per kapita", None, "gni_per_kapita_usd")
# indikator harga punya 3 satuan (USD/GNIpc/PPP) untuk nama yang sama -> WAJIB filter satuan,
# pakai GNIpc karena itu standar internasional (ITU/UN Broadband Commission) untuk keterjangkauan
harga_mm    = ambil(dunia, "Data-only mobile broadband 2GB (2021-2024)", "GNIpc", "harga_data_persen_gni")
listrik_mm  = ambil(dunia, "Penduduk dengan akses listrik", None, "akses_listrik_persen")
pend_mm     = ambil(dunia, "Angka partisipasi kasar pendidikan menengah", None, "partisipasi_pendidikan_persen")
urban_mm    = ambil(dunia, "Penduduk yang tinggal di wilayah perkotaan", None, "urbanisasi_persen")

tabel_mm = reduce(
    lambda l, r: pd.merge(l, r, on=["kode_wilayah", "nama_wilayah", "tahun"], how="outer"),
    [internet_mm, gni_mm, harga_mm, listrik_mm, pend_mm, urban_mm],
)
tabel_mm["is_indonesia"] = tabel_mm["kode_wilayah"] == "IDN"
tabel_mm["is_asean"] = tabel_mm["kode_wilayah"].isin(ASEAN_CODES)
tabel_mm = tabel_mm.sort_values(["tahun", "nama_wilayah"])

lengkap_mm = tabel_mm.dropna(subset=[
    "pengguna_internet_persen", "gni_per_kapita_usd", "harga_data_persen_gni",
    "akses_listrik_persen", "partisipasi_pendidikan_persen", "urbanisasi_persen",
])
print(f"\n=== Tabel Makro-Mikro Dunia (6 faktor) ===")
print("Shape:", tabel_mm.shape)
print("Baris dengan SEMUA 6 kolom lengkap:", lengkap_mm.shape[0])
print("CATATAN: kolom harga_data_persen_gni cuma ada 2021-2024, jadi analisis")
print("6-faktor lengkap sebaiknya dibatasi ke rentang tahun itu saja.")

tabel_mm.to_csv(OUT_DIR / "dataset_dunia_makro_mikro.csv", index=False, encoding="utf-8-sig")
print("Tersimpan:", OUT_DIR / "dataset_dunia_makro_mikro.csv")
