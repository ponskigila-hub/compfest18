# -*- coding: utf-8 -*-
"""
clean_data.py
=============
Skrip cleaning untuk dashboard COMPFEST 18:
"Menakar Posisi Keterjangkauan Internet Indonesia di Tingkat ASEAN serta
Dampaknya terhadap Kesenjangan Pemanfaatan Digital Antarprovinsi"

Input  : raw_data_asli/dataset_asia_tenggara.csv
         raw_data_asli/dataset_indonesia.csv
Output : output_bersih/dataset_asia_tenggara_clean.csv
         output_bersih/dataset_indonesia_clean.csv
         output_bersih/mapping_jawa_luar_jawa.csv
         output_bersih/log_cleaning.txt

Cara pakai:
    pip install pandas --break-system-packages   # jika belum ada
    python clean_data.py
"""

import pandas as pd
import numpy as np
from pathlib import Path

IN_DIR = Path("../01_raw_data")
OUT_DIR = Path("../03_clean_data")
OUT_DIR.mkdir(exist_ok=True)

log_lines = []
def log(msg):
    print(msg)
    log_lines.append(str(msg))


# =====================================================================
# 1. LOAD — selalu pakai encoding utf-8-sig karena file punya BOM (﻿)
# =====================================================================
def load_csv(path):
    df = pd.read_csv(path, encoding="utf-8-sig", dtype=str)
    # trim whitespace di semua kolom string (jaga-jaga ada spasi nyasar)
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].str.strip()
    return df

df_asean = load_csv(IN_DIR / "dataset_asia_tenggara.csv")
df_id    = load_csv(IN_DIR / "dataset_indonesia.csv")

# kembalikan tipe data numerik yang sesuai
df_asean["tahun"] = df_asean["tahun"].astype(int)
df_asean["nilai"] = df_asean["nilai"].astype(float)

df_id["tahun"] = df_id["tahun"].astype(int)
df_id["nilai"] = df_id["nilai"].astype(float)
df_id["kode_wilayah"] = df_id["kode_wilayah"].astype(int)

log(f"Dataset ASEAN awal : {df_asean.shape[0]} baris, {df_asean.shape[1]} kolom")
log(f"Dataset Indonesia awal : {df_id.shape[0]} baris, {df_id.shape[1]} kolom")


# =====================================================================
# 2. FIX — standardisasi nama negara ASEAN (kasus "Lao P.D.R." vs "Lao PDR")
# =====================================================================
# Sumber kebenaran: kode_wilayah (ISO3), bukan nama_wilayah, karena nama
# teks bisa berubah antar-vintage sumber data (ITU vs World Bank).
nama_negara_standar = {
    "BRN": "Brunei Darussalam",
    "IDN": "Indonesia",
    "KHM": "Cambodia",
    "LAO": "Laos",              # sebelumnya: "Lao P.D.R." & "Lao PDR" -> disatukan
    "MMR": "Myanmar",
    "MYS": "Malaysia",
    "PHL": "Philippines",
    "SGP": "Singapore",
    "THA": "Thailand",
    "TLS": "Timor-Leste",
    "VNM": "Viet Nam",
}
sebelum = df_asean["nama_wilayah"].nunique()
df_asean["nama_wilayah"] = df_asean["kode_wilayah"].map(nama_negara_standar)
sesudah = df_asean["nama_wilayah"].nunique()
log(f"Standarisasi nama negara ASEAN: {sebelum} -> {sesudah} nama unik "
    f"(khusus Laos: 'Lao P.D.R.' & 'Lao PDR' -> 'Laos')")

# kolom versi_wilayah 100% kosong untuk dataset ASEAN -> tidak relevan, dibuang
df_asean = df_asean.drop(columns=["versi_wilayah"])


# =====================================================================
# 3. FIX — buat kunci indikator yang benar-benar unik
# =====================================================================
# kode_indikator TIDAK unik (mis. 'percentage_users' dipakai untuk dua
# indikator berbeda: "Tujuan penggunaan internet" dan
# "Perangkat yang digunakan untuk mengakses internet").
# Solusi: buat kolom baru `id_indikator_unik` = kode_indikator + topik.
df_id["id_indikator_unik"] = df_id["kode_indikator"] + " | " + df_id["topik"]
df_asean["id_indikator_unik"] = df_asean["kode_indikator"] + " | " + df_asean["topik"]

cek = df_id.groupby("kode_indikator")["nama_indikator"].nunique()
ambigu = cek[cek > 1]
log(f"\nkode_indikator yang tidak unik di dataset Indonesia (perlu id_indikator_unik): "
    f"{list(ambigu.index)}")


# =====================================================================
# 4. FIX — tandai cakupan wilayah (34 vs 38 provinsi) supaya tren tidak
#    salah dibaca akibat pemekaran Papua di 2024
# =====================================================================
def cakupan_provinsi(v):
    if v == "id_38_2024":
        return 38
    else:
        return 34  # id_34_pre_split & id_34_papua_aggregated_2023_2024

df_id["cakupan_jumlah_provinsi"] = df_id["versi_wilayah"].apply(cakupan_provinsi)

log("\nDistribusi versi_wilayah per tahun (untuk cek konsistensi tren):")
log(str(pd.crosstab(df_id["tahun"], df_id["versi_wilayah"])))
log(
    "\nCATATAN PENTING:\n"
    "- 2017-2022 & sebagian besar topik 2023 -> 34 provinsi lama (Papua & Papua Barat belum pecah)\n"
    "- 2024 topik 'Pembangunan TIK' & 'Komponen pembangunan TIK' -> tetap 34 provinsi "
    "  (6 provinsi baru di Papua sudah diagregasikan balik oleh sumber data / BPS)\n"
    "- 2024 topik lain (Akses internet, Akses rumah tangga, Kesenjangan gender, "
    "  Perangkat akses, Pemanfaatan internet) -> 38 provinsi (Papua sudah pecah)\n"
    "- Untuk GARIS TREN 2017-2024 yang mulus, gunakan agregasi 34 provinsi "
    "  (kelompokkan 6 provinsi pecahan Papua kembali ke 'Papua'/'Papua Barat' -> lihat kolom "
    "  provinsi_induk_34 di bawah).\n"
    "- Untuk SNAPSHOT/PETA tahun 2024 paling detail, gunakan versi 38 provinsi apa adanya."
)


# =====================================================================
# 5. TAMBAH — kolom provinsi_induk_34 (untuk konsistensi tren jangka panjang)
# =====================================================================
provinsi_induk_34 = {
    "Papua Barat Daya": "Papua Barat",
    "Papua Pegunungan": "Papua",
    "Papua Selatan": "Papua",
    "Papua Tengah": "Papua",
}
df_id["provinsi_induk_34"] = df_id["nama_wilayah"].map(provinsi_induk_34).fillna(df_id["nama_wilayah"])


# =====================================================================
# 6. TAMBAH — kolom region_group (Jawa vs Luar Jawa) untuk Area 2
# =====================================================================
provinsi_jawa = {
    "DKI Jakarta", "Jawa Barat", "Jawa Tengah",
    "DI Yogyakarta", "Jawa Timur", "Banten",
}
df_id["region_group"] = np.where(
    df_id["nama_wilayah"].isin(provinsi_jawa), "Jawa", "Luar Jawa"
)
# gunakan provinsi_induk_34 juga untuk grouping supaya provinsi pecahan Papua
# otomatis konsisten masuk "Luar Jawa"
log(f"\nDistribusi region_group: {df_id['region_group'].value_counts().to_dict()}")

# simpan tabel mapping sebagai referensi terpisah (dipakai juga di dashboard)
mapping_rows = []
for p in sorted(df_id["nama_wilayah"].unique()):
    mapping_rows.append({
        "nama_wilayah": p,
        "region_group": "Jawa" if p in provinsi_jawa else "Luar Jawa",
        "provinsi_induk_34": provinsi_induk_34.get(p, p),
    })
df_mapping = pd.DataFrame(mapping_rows)
df_mapping.to_csv(OUT_DIR / "mapping_jawa_luar_jawa.csv", index=False)


# =====================================================================
# 7. FIX — isi NaN di kolom disagregasi dengan label eksplisit
#    (biar tidak jadi blank/None yang bikin filter di BI tool berantakan)
# =====================================================================
kolom_disagregasi = [
    "jenis_disagregasi_1", "kategori_disagregasi_1",
    "jenis_disagregasi_2", "kategori_disagregasi_2",
]
for col in kolom_disagregasi:
    df_id[col] = df_id[col].fillna("tidak_ada")
    df_asean[col] = df_asean[col].fillna("tidak_ada")


# =====================================================================
# 8. FLAG — pisahkan data Literasi Digital (snapshot 2021, one-off)
#    sesuai keputusan: tidak masuk tren utama, jadi info box statis saja
# =====================================================================
mask_literasi = df_id["dataset_asal"] == "kominfo_digital_literacy_province_2021"
df_id["kategori_pemakaian"] = np.where(
    mask_literasi, "snapshot_statis_2021", "tren_utama"
)
log(f"\nJumlah baris data Literasi Digital (snapshot 2021, dipisah dari tren utama): "
    f"{mask_literasi.sum()}")


# =====================================================================
# 9. VALIDASI AKHIR
# =====================================================================
key_cols = ["kode_wilayah", "tahun", "id_indikator_unik",
            "jenis_disagregasi_1", "kategori_disagregasi_1",
            "jenis_disagregasi_2", "kategori_disagregasi_2"]
dup_id = df_id.duplicated(subset=key_cols).sum()
dup_asean = df_asean.duplicated(subset=key_cols).sum()
log(f"\nCek duplikat setelah cleaning (pakai id_indikator_unik):")
log(f"  Dataset Indonesia : {dup_id} baris duplikat")
log(f"  Dataset ASEAN     : {dup_asean} baris duplikat")

log(f"\nCek nilai kosong/null di kolom 'nilai':")
log(f"  Dataset Indonesia : {df_id['nilai'].isna().sum()}")
log(f"  Dataset ASEAN     : {df_asean['nilai'].isna().sum()}")

log(f"\nRentang nilai kolom 'nilai':")
log(f"  Indonesia : min={df_id['nilai'].min()}, max={df_id['nilai'].max()}")
log(f"  ASEAN     : min={df_asean['nilai'].min()}, max={df_asean['nilai'].max()}")


# =====================================================================
# 10. EXPORT
# =====================================================================
df_asean.to_csv(OUT_DIR / "dataset_asia_tenggara_clean.csv", index=False, encoding="utf-8-sig")
df_id.to_csv(OUT_DIR / "dataset_indonesia_clean.csv", index=False, encoding="utf-8-sig")

log(f"\n✅ Selesai. File bersih tersimpan di folder '{OUT_DIR}/':")
log(f"   - dataset_asia_tenggara_clean.csv ({df_asean.shape[0]} baris, {df_asean.shape[1]} kolom)")
log(f"   - dataset_indonesia_clean.csv ({df_id.shape[0]} baris, {df_id.shape[1]} kolom)")
log(f"   - mapping_jawa_luar_jawa.csv ({df_mapping.shape[0]} baris)")

with open(OUT_DIR / "log_cleaning.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(log_lines))
