# Paket Data — Dashboard COMPFEST 18 Data Analytics Dash

**Topik**: "Mendiagnosis Kesenjangan Digital Indonesia: Analisis Komparatif Multi-Faktor
Adopsi Internet terhadap Negara-Negara Dunia"

**Struktur dashboard**: Makro (posisi Indonesia vs dunia) → Mikro (perbandingan head-to-head
Indonesia vs 1 negara pembanding pilihan bebas, dibedah lewat 5 faktor struktural)

---

## Struktur Folder

```
01_raw_data/            Data mentah asli dari panitia + dataset_dunia.csv (arsip, jangan diubah)
02_scripts/               Script Python untuk reproduksi seluruh proses cleaning & tabel dashboard
03_clean_data/             Output cleaning (dataset penuh, sudah dibersihkan, level negara/provinsi)
04_ready_for_dashboard/    Tabel siap-pakai untuk visual utama di Power BI
05_dokumentasi/            File ini
```

## Urutan Menjalankan Ulang (kalau perlu reproduksi dari awal)

```
cd 02_scripts
python clean_data.py              # 01_raw_data -> 03_clean_data (Indonesia & ASEAN)
python verify_data.py             # validasi 03_clean_data (harus semua [PASS])
python build_dashboard_tables.py  # 03_clean_data + 01_raw_data -> 04_ready_for_dashboard
```

`build_dashboard_tables.py` butuh `01_raw_data/dataset_dunia.csv` (untuk 2 tabel dunia)
dan `03_clean_data/dataset_indonesia_clean.csv` (untuk tabel gap provinsi) — jalankan
`clean_data.py` dulu sebelum `build_dashboard_tables.py`.

---

## File yang di-load ke Power BI

| File | Untuk Halaman | Isi & Cara Dibuat |
|---|---|---|
| `04_ready_for_dashboard/dataset_dunia_makro_mikro.csv` | **Halaman 1 (Makro) & Halaman 2 (Mikro)** — dipakai utama | 1 baris = 1 negara-tahun. 6 kolom faktor: `pengguna_internet_persen`, `gni_per_kapita_usd`, `harga_data_persen_gni`, `akses_listrik_persen`, `partisipasi_pendidikan_persen`, `urbanisasi_persen`, plus flag `is_indonesia`/`is_asean`. Dibuat dengan mengambil 6 indikator dari `dataset_dunia.csv` (filter per `nama_indikator`, khusus harga difilter juga `satuan == "GNIpc"`), lalu di-merge jadi satu tabel wide per negara-tahun. |
| `04_ready_for_dashboard/scatter_dunia_gni_internet.csv` | Cadangan (scatter GNI-only) | Versi 2-kolom (GNI, pengguna internet) dari 201 negara — subset dari tabel makro-mikro di atas, disimpan terpisah kalau cuma butuh 2 sumbu. |
| `04_ready_for_dashboard/scatter_asean_gni_internet.csv` | Cadangan/referensi | Versi 11 negara ASEAN saja (dari eksplorasi awal, tidak lagi jadi fokus utama). |
| `04_ready_for_dashboard/gap_rural_urban_provinsi.csv` | Opsional (jika Indonesia-provinsi tetap ditampilkan sebagai suplemen) | Gap akses rural-urban per provinsi-tahun, dari `dataset_indonesia_clean.csv` topik "Akses internet", di-pivot per kategori rural/urban lalu dihitung `gap_rural_urban_pp = urban - rural`. |
| `03_clean_data/dataset_indonesia_clean.csv` | Opsional (suplemen provinsi) | Data provinsi lengkap, sudah ada `id_indikator_unik`, `provinsi_induk_34`, `region_group`. |
| `03_clean_data/dataset_asia_tenggara_clean.csv` | Cadangan/referensi | Data 11 negara ASEAN, nama negara sudah dinormalisasi berdasarkan `kode_wilayah`. |

## Cara Tabel `dataset_dunia_makro_mikro.csv` Dibuat (ringkas)

```python
# 1. Normalisasi nama negara di dataset_dunia.csv berdasarkan kode_wilayah (ISO3),
#    karena 250 label nama ternyata cuma 217 negara/wilayah unik secara kode
#    (mis. "Lao PDR"/"Lao P.D.R.", "Turkiye"/"Türkiye")
canon_name = dunia.groupby("kode_wilayah")["nama_wilayah"].agg(lambda x: sorted(x.unique())[0])
dunia["nama_wilayah"] = dunia["kode_wilayah"].map(canon_name)

# 2. Ambil 6 indikator, masing-masing di-filter nama_indikator (dan satuan khusus utk harga)
#    lalu di-merge (outer join) jadi satu tabel wide per kode_wilayah + tahun
```

Lihat kode lengkapnya di `02_scripts/build_dashboard_tables.py`, bagian "TABEL 4".

---

## Catatan Penting yang WAJIB masuk Dokumen Deskripsi

1. **Indikator harga (`Data-only mobile broadband 2GB`) punya 3 satuan berbeda** untuk nama
   indikator yang sama: USD, GNIpc (harga sebagai % pendapatan per kapita), dan PPP. Tabel ini
   memakai **GNIpc** karena itu standar internasional keterjangkauan (ITU/UN Broadband
   Commission, ambang batas 2%). Kalau filter cuma pakai `nama_indikator` tanpa `satuan`,
   datanya tercampur 3x lipat.
2. **Kolom harga cuma tersedia 2021–2024** — baris dengan SEMUA 6 kolom terisi (tanpa NaN)
   cuma 481 dari total baris tabel, dan terkonsentrasi di rentang tahun itu. Batasi analisis
   6-faktor lengkap ke 2021–2024, jangan tarik ke tahun-tahun sebelumnya.
3. **Nama negara dinormalisasi berdasarkan `kode_wilayah` (ISO3)**, bukan teks nama — berlaku
   di seluruh dataset dunia (250 label nama → 217 negara/wilayah unik secara kode) maupun
   ASEAN (Lao PDR/Lao P.D.R. → Laos).
4. **Negara pembanding di dashboard dipilih bebas oleh pengguna** (tidak difilter otomatis
   berdasarkan kemiripan GNI/populasi) — pastikan rumusan masalah & tujuan di laporan
   konsisten dengan ini (lihat versi final di histori chat).
5. Jika bagian provinsi Indonesia tetap dipakai sebagai suplemen: batas wilayah tidak seragam
   antar topik (38 vs 34 provinsi pasca-pemekaran Papua) — kolom `provinsi_induk_34` disediakan
   untuk analisis tren konsisten; agregasinya **tidak berbobot populasi** (data populasi tidak
   tersedia di dataset ini).
6. **`kode_indikator` tidak unik lintas topik** di `dataset_indonesia_clean.csv` — gunakan
   `id_indikator_unik` (topik + kode_indikator) untuk semua join/filter.

## Temuan Awal yang Sudah Tervalidasi (bisa dipakai di draf presentasi)

- **Indonesia 2024**: pengguna internet 72,8%, GNI $4.920, harga data 2GB = **0,49% dari GNI**
  (jauh di bawah ambang batas keterjangkauan PBB 2%), akses listrik 99,9%, partisipasi
  pendidikan menengah 98,8%, urbanisasi 58,8% — pola ini menunjukkan keterjangkauan harga dan
  infrastruktur dasar Indonesia sudah relatif baik, sehingga gap adopsi internet kemungkinan
  besar dijelaskan oleh faktor lain, bukan semata ekonomi/infrastruktur.
- Data 6-faktor lengkap tersedia untuk 95–134 negara per tahun (2021–2024) — cukup luas untuk
  perbandingan head-to-head dengan negara manapun yang dipilih pengguna.
