# 🌍 Global Digital Landscape & Indonesia's Position
*Multi-Page Executive Business Intelligence Dashboard built in Power BI*

---

## 📌 1. Tentang Proyek Ini
Proyek ini adalah *dashboard* analitik interaktif berbasis Power BI yang dirancang secara komprehensif dalam dua halaman untuk memetakan dan membandingkan **lanskap digital global, pertumbuhan adopsi internet, faktor pendukung struktural (*structural enablers*), serta posisi strategis Indonesia** baik di kancah global maupun regional ASEAN.

---

## 📂 2. Daftar File yang Harus Disiapkan
Agar seluruh *dashboard* (Halaman 1 dan Halaman 2) dapat dibuka, dijalankan, dan diuji coba dengan sempurna di Power BI Desktop, pastikan file-file berikut sudah disiapkan di dalam satu folder yang sama:

1. **`dataset_final_halaman_utama.csv`**
   * **Fungsi:** Sumber data utama untuk **Halaman 1 (Page 1)**.
   * **Isi:** Berisi 2.790 baris data historis global (*time-series*) yang mencakup penetrasi internet, GNI per kapita, populasi, dan kategori pendapatan (*High Income*, dll.).
2. **`dataset_dunia_makro_mikro.csv`**
   * **Fungsi:** Sumber data utama untuk **Halaman 2 (Page 2)**.
   * **Isi:** Berisi 3.472 baris data historis global yang memperdalam indikator struktural seperti keterjangkauan harga data, akses listrik, urbanisasi, dan partisipasi pendidikan.
3. **File Proyek Power BI Utama (`.pbix`)**
   * File kerja Power BI tempat laporan Halaman 1 dan Halaman 2 diintegrasikan.

---

## 🖥️ 3. Arsitektur & Isi Halaman Dashboard

### **Halaman 1 (Page 1): Global Landscape & Indonesia's Position**
Fokus pada perbandingan makro eksekutif dan posisi Indonesia secara interaktif:
* **Slicer & KPI Cards:** Filter interaktif Tahun (2010–2024) dan Nama Negara, dilengkapi ringkasan angka global dan total populasi.
* **Peta Global & Narasi Dinamis:** Peta dunia interaktif dengan kotak narasi otomatis yang beradaptasi saat negara dipilih.
* **Scatter Plot (GNI per Capita vs Internet Users):** Dilengkapi garis acuan kuadran analitis dan warna berdasarkan kelompok pendapatan (*Income Group*).
* **Internet Users Comparison:** Bar chart perbandingan (*Top Global*, *Average Global*, *Selected Country*, *Indonesia*, *Bottom Global*) lengkap dengan *Reference Line* rata-rata dunia.
* **ASEAN Access Ranking:** Grafik peringkat penetrasi internet khusus kawasan ASEAN.
* **Digital Adoption Trajectory:** Tren historis pertumbuhan internet 2010–2024.
* **Quick Summary Badges:** Kartu ringkasan mini untuk status peringkat global dan kelompok pendapatan negara pilihan.

### **Halaman 2 (Page 2): Deep-Dive Analysis & Structural Enablers**
Fokus pada analisis mendalam mengenai faktor pendorong di balik adopsi digital:
* **Analisis Keterjangkauan Harga Data:** Mengkaji korelasi biaya paket data seluler terhadap GNI per kapita.
* **Infrastruktur Dasar (Akses Listrik):** Memetakan ketersediaan listrik sebagai fondasi utama adopsi teknologi.
* **Faktor Demografi & Urbanisasi:** Meneliti pengaruh tingkat urbanisasi terhadap transformasi digital.
* **Matriks Tabel Rinci:** Tabel komprehensif dengan *conditional formatting* untuk eksplorasi data secara transparan.

---

## 🛠️ 4. Strategi Pengelolaan Data & Missing Value
* **Halaman 1:** Menggunakan data bersih yang telah diagregasi untuk metrik perbandingan global dan regional.
* **Halaman 2:** Baris data dengan *missing value* (seperti data harga data yang tidak dilaporkan sebagian negara) **tidak dihapus** dari tabel agar data penting lainnya di baris yang sama (seperti internet dan GNI) tetap aman. Power BI secara otomatis mengabaikan nilai kosong (*blank*) pada visualisasi.

---

## 🚀 5. Cara Menjalankan Proyek
1. Buka aplikasi **Power BI Desktop**.
2. Buka file proyek `.pbix` utama.
3. Jika direktori sumber data berubah, masuk ke menu **Home** -> **Transform Data** (Power Query).
4. Pastikan file sumber diarahkan kembali ke **`dataset_final_halaman_utama.csv`** dan **`dataset_dunia_makro_mikro.csv`**.
5. Klik **Apply Changes** untuk memuat seluruh data ke dalam laporan.