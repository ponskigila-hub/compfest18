# Paket Data — Dashboard "Menakar Posisi Keterjangkauan Internet Indonesia di Tingkat ASEAN
# serta Dampaknya terhadap Kesenjangan Pemanfaatan Digital Antarprovinsi"

Data Analytics Dash — COMPFEST 18

## Struktur Folder

```
01_raw_data/            Data mentah asli dari panitia (jangan diubah, jadi arsip)
02_scripts/              Script Python untuk reproduksi seluruh proses cleaning
03_clean_data/            Output cleaning (dataset penuh, sudah dibersihkan)
04_ready_for_dashboard/   Tabel siap-pakai untuk 2 visual utama di Power BI
05_dokumentasi/           File ini + catatan keputusan preprocessing
```

## Urutan Menjalankan Ulang (kalau perlu reproduksi dari awal)

```
cd 02_scripts
python clean_data.py              # 01_raw_data -> 03_clean_data
python verify_data.py             # validasi 03_clean_data (harus semua PASS)
python build_dashboard_tables.py  # 03_clean_data -> 04_ready_for_dashboard
```

## File yang langsung di-load ke Power BI

| File | Untuk Halaman | Isi |
|---|---|---|
| `03_clean_data/dataset_indonesia_clean.csv` | Semua (raw model) | Data provinsi lengkap, sudah ada `id_indikator_unik`, `provinsi_induk_34`, `region_group` |
| `03_clean_data/dataset_asia_tenggara_clean.csv` | Cadangan/referensi | Data 11 negara ASEAN, nama negara sudah dinormalisasi |
| `04_ready_for_dashboard/scatter_dunia_gni_internet.csv` | **Halaman 1 (Macro)** — dipakai | GNI per kapita vs Pengguna internet, 201 negara, dengan flag `is_indonesia` & `is_asean` untuk highlight |
| `04_ready_for_dashboard/scatter_asean_gni_internet.csv` | Cadangan/referensi | Versi 11 negara ASEAN saja (disimpan sebagai pembanding, tidak lagi dipakai utama) |
| `04_ready_for_dashboard/gap_rural_urban_provinsi.csv` | Halaman 2 & 3 (Micro/Policy) | Gap akses rural-urban per provinsi-tahun, sudah dihitung |

**Catatan pergantian scope**: dashboard ini sekarang membandingkan Indonesia dengan **dunia** (201 negara), bukan cuma ASEAN. Konsekuensinya: judul dashboard & laporan perlu disesuaikan (tidak lagi "...di Tingkat ASEAN..."), dan disarankan pakai kolom `is_indonesia`/`is_asean` untuk highlight visual, karena 201 titik scatter tanpa highlight akan sulit dibaca juri dalam waktu presentasi 10 menit.

## Catatan Penting yang WAJIB masuk Dokumen Deskripsi

1. **Batas wilayah tidak seragam antar topik** — sebagian topik pakai 38 provinsi (2024, pasca-pemekaran Papua), sebagian pakai 34 provinsi lama. Kolom `provinsi_induk_34` disediakan untuk analisis tren jangka panjang yang konsisten; kolom `nama_wilayah` asli dipakai untuk snapshot/peta detail 2024.
2. **Agregasi provinsi Papua ke `provinsi_induk_34` tidak berbobot populasi** — dataset ini tidak menyediakan data populasi, jadi rata-rata antar provinsi pecahan Papua dihitung tanpa bobot. Sebutkan ini sebagai keterbatasan.
3. **`kode_indikator` tidak unik lintas topik** — gunakan `id_indikator_unik` (topik + kode_indikator) untuk semua join/filter, jangan `kode_indikator` sendirian.
4. **Data Literasi Digital hanya snapshot 2021** (34 provinsi lama) — ditandai `kategori_pemakaian = "snapshot_statis_2021"`, sengaja dipisah dari tren utama, disarankan hanya jadi info box statis di dashboard, bukan bagian tren.
5. **Scatter ASEAN**: tahun 2025 dan sebagian tahun Myanmar/Timor-Leste tidak punya data pengguna internet lengkap — batasi visual sampai 2024 untuk data yang solid.
6. **DKI Jakarta tidak punya nilai akses rural** — wajar (100% wilayah urban), bukan data hilang; gap rural-urban untuk DKI Jakarta secara logis tidak terdefinisi.
7. **Nama negara dinormalisasi berdasarkan `kode_wilayah` (ISO3)**, bukan teks nama — berlaku untuk ASEAN maupun dunia. Di dataset dunia, 250 label nama ternyata cuma 217 negara/wilayah unik secara kode (contoh: "Lao PDR"/"Lao P.D.R.", "Turkiye"/"Türkiye", "Venezuela"/"Venezuela, RB").
8. **Scatter dunia**: tahun 2025 baru punya data pengguna internet untuk 9 negara — batasi visual sampai 2024 sama seperti scatter ASEAN.

## Temuan Awal yang Sudah Tervalidasi (bisa langsung dipakai di draf presentasi)

- Gap rural-urban terbesar 2024: **Papua Tengah (70,3 pp)**, Papua Selatan (40,5 pp), Papua (38,2 pp), Papua Pegunungan (37,7 pp), NTT (30,2 pp) — 4 dari 5 gap terbesar ada di provinsi pecahan Papua.
- Data GNI-vs-pengguna internet ASEAN lengkap untuk 158 dari 176 kombinasi negara-tahun (2010-2024); jangan pakai 2025 karena banyak bolong.
