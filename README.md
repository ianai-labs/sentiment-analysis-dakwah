<!-- Badge Section -->
<p align="left">
  <img src="https://img.shields.io/badge/Python-3.9+-blue?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/TensorFlow-2.x-orange?logo=tensorflow&logoColor=white" alt="TensorFlow">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/Status-Active-brightgreen" alt="Status">
</p>

# Analisis Sentimen Komentar Dakwah Islam (LSTM / BiLSTM / GRU)

Proyek ini bertujuan untuk mengklasifikasikan sentimen komentar YouTube pada topik **Dakwah Islam Indonesia** ke dalam tiga kelas: **Negatif (0)**, **Netral (1)**, dan **Positif (2)**.  

Metode pelabelan menggunakan ensemble **Lexicon (InSet + domain dakwah) + SVM** untuk menghasilkan label berkualitas tinggi. Selanjutnya, tiga skema deep learning dilatih dan dibandingkan:
<br>Pelabelan Otomatis — Lexicon + Ensemble SVM
- **Skema 1:** LSTM + Trainable Embedding (split 80/20)
- **Skema 2:** BiLSTM + Trainable Embedding (split 80/20)
- **Skema 3:** GRU + Trainable Embedding (split 70/30)

---

## 📁 Struktur File
`├──` proyek_analisis_sentimen_opini.ipynb  # Notebook utama (preprocessing, training, evaluasi, inference)<br>
`├──` opini-dakwah-islam.csv                # Dataset final (komentar + label)<br>
`├──` scraper.py                            # Script scraping komentar YouTube (opsional)<br>
`├──` requirements.txt                      # Daftar library yang diperlukan<br>
`└──` README.md                             # File ini<br>

---

## 🚀 Cara Menjalankan di Google Colab (Rekomendasi)

1. **Buka notebook** di Google Colab:  
   `File → Upload notebook` → pilih `proyek_analisis_sentimen_opini.ipynb`

2. **Upload dataset** ke lingkungan Colab:  
   - Klik ikon folder di sidebar kiri  
   - Klik **Upload** → pilih `opini-dakwah-islam.csv`

3. **Jalankan semua cell** secara berurutan (`Runtime → Run all`).

> **Catatan:** Jika ada error karena library belum terinstall, jalankan cell berikut di awal notebook:  
> `!pip install -q gensim wordcloud sastrawi`

---

## 🖥️ Cara Menjalankan di Lokal (Python + Jupyter)

1. **Clone repository ini** (atau unduh semua file).
2. **Buka terminal** di folder proyek.
3. **Buat virtual environment** (opsional tapi disarankan):
   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows
4. **Install dependencies:** pip install -r requirements.txt
5. **Jalankan Jupyter:** jupyter notebook
6. Buka proyek_analisis_sentimen_opini.ipynb dan jalankan cell.

---

📂 Menggunakan Dataset Sendiri
Jika Anda ingin menggunakan dataset komentar Anda sendiri (bukan opini-dakwah-islam.csv), ikuti langkah berikut:

Persyaratan dataset:
File CSV wajib memiliki kolom:
**comment** : teks komentar (string)

Langkah menggunakan dataset sendiri:
1. Letakkan file CSV Anda di folder yang sama dengan notebook.
2. Pada cell load dataset (bagian 2), ubah nama file menjadi file Anda: **df = pd.read_csv('nama_file_anda.csv')**
3. astikan kolom comment dan source_sentiment tersedia. Jika nama kolom berbeda, sesuaikan di bagian mapping label.
4. Jalankan seluruh notebook seperti biasa.
   Catatan: Semakin banyak data, semakin baik performa model
   (minimal 5000 baris disarankan). Pastikan distribusi label relatif seimbang.

---

📊 Hasil Akhir
Setelah menjalankan notebook, Anda akan mendapatkan:

1. Visualisasi EDA (distribusi label, wordcloud, histogram panjang teks)
2. Tiga model terlatih (LSTM, BiLSTM, GRU)
3. Confusion matrix dan learning curves untuk setiap model
4. Perbandingan akurasi antar skema
5. Fungsi inference untuk memprediksi sentimen teks baru
---

## 🧠 Technical Insights & Methodology

Selama pengembangan proyek ini, saya menghadapi dan menyelesaikan beberapa tantangan teknis. Berikut adalah pembelajaran utama yang saya peroleh:

### 1. Pelabelan Otomatis dengan Ensemble Lexicon + SVM
- **Tantangan:** Pelabelan manual untuk ribuan komentar tidak mungkin. Lexicon InSet generik kurang sensitif terhadap kosakata dakwah.
- **Solusi:**  
  - Menambahkan **domain lexicon khusus dakwah** (positif/negatif/netral) dan **bigram lexicon** untuk menangkap frasa.  
  - Membangun **ensemble konservatif**: hanya sampel di mana lexicon dan SVM sepakat yang dipertahankan. Ini mengurangi noise label secara signifikan.

### 2. Mengatasi Ketidakseimbangan Kelas
- **Masalah:** Kelas netral hanya ~19%, sementara positif ~44% dan negatif ~36%.  
- **Strategi:**  
  - Menggunakan `class_weight='balanced'` pada SVM dan **class_weight** pada model deep learning.  
  - Split data dengan `stratify=y` untuk menjaga proporsi kelas.

### 3. Regularisasi Kuat untuk Cegah Overfitting
- **Observasi:** Dengan ~13.000 sampel, model RNN (LSTM/BiLSTM/GRU) mudah overfitting.  
- **Implementasi:**  
  - `SpatialDropout1D(0.45)` setelah embedding.  
  - `Dropout(0.45)` pada dense layer.  
  - **Recurrent dropout (0.25)** di dalam sel RNN.  
  - **L2 regularizer** (0.005–0.01) pada kernel.  
  - Arsitektur sederhana: hanya 32 unit (bukan 128/64) agar sesuai ukuran data.

### 4. Optimasi Hyperparameter (Iterative Tuning)
- Proses trial and error mencakup:  
  - Learning rate (0.0005, 0.001, 0.0006)  
  - Dropout rates (0.3 → 0.45)  
  - Batch size (64 → 128)  
  - Panjang sequence (50 → 150)  
  - Dimensi embedding (64 → 128)  

### 5. Preprocessing untuk Bahasa Indonesia
- **Tantangan:** Slang, ejaan tidak baku, campuran Inggris-Indonesia, kata serapan asing.  
- **Pipeline:**  
  - Lowercase, hapus non-alfabet.  
  - Stopword removal (daftar kustom + bawaan Sastrawi).  
  - Stemming Sastrawi untuk normalisasi kata.  
  - Pembersihan lanjutan: hapus kata konsonan-only dan kata dengan huruf v,z,q,x (sering typo/asing).  
- **Trade-off:** Preprocessing agresif mengurangi ukuran vocabulary tetapi meningkatkan generalisasi.

### 6. Callback Strategy
- **Early Stopping** (patience=2, monitor `val_loss`) untuk menghentikan training saat validasi stagnan.  
- **ReduceLROnPlateau** (factor 0.5, patience=1) untuk menurunkan learning rate otomatis.  
- Callback di-**reinit** per skema → hasil fair dan reproducible.

### 7. Pembelajaran Kunci
- **Kualitas label > kompleksitas model** – ensemble labeling lebih berdampak daripada menambah layer.  
- **Regularisasi harus proporsional dengan ukuran data** – untuk ~13k sampel, dropout 0.45 diperlukan; dataset lebih besar akan butuh dropout lebih rendah.  
- **BiLSTM sedikit lebih unggul** dari LSTM karena konteks bidirectional, namun GRU menawarkan kecepatan training sebanding dengan akurasi hampir sama.  
- **Validasi accuracy plateau** di epoch 11–12, early stopping mencegah overfitting.

### 8. Potensi Pengembangan Lanjutan
- Gunakan **IndoBERT pre-trained** untuk representasi konteks lebih kaya (jika komputasi memadai).  
- Perbanyak data (target 50k+) untuk meningkatkan generalisasi.  
- **Cross-validation (k-fold)** untuk evaluasi lebih robust.  
- **Data augmentation** (back-translation, synonym replacement) untuk menyeimbangkan kelas minoritas.

---

👤 Kontributor
[Dibuat untuk keperluan tugas proyek Proyek Analisis Sentimen
  dicoding.com : Belajar Fundamental Deep Learning]
