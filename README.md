# E-Commerce Public Dataset Analytics Dashboard 

Proyek akhir Analisis Data menggunakan **E-Commerce Public Dataset** (Olist) yang mencakup proses Data Wrangling, Exploratory Data Analysis (EDA), segmentasi pelanggan menggunakan RFM Analysis, serta dashboard interaktif berbasis Streamlit.

- **Live Dashboard:** [https://dashboard-satria.streamlit.app](https://dashboard-satria.streamlit.app)

## Struktur Direktori
```text
├── Dashboard/
│   ├── dashboard.py
│   └── main_data.csv
├── data/
│   └── (9 file dataset mentah .csv)
├── notebook.ipynb
├── README.md
├── requirements.txt
└── url.txt
```

## Pertanyaan Bisnis
1. Bagaimana tren pertumbuhan jumlah pesanan dan total pendapatan (*revenue*) bulanan pada periode Januari 2017 hingga Agustus 2018, serta 10 kategori produk apa saja yang menghasilkan total pendapatan tertinggi dan terendah untuk menentukan prioritas stok dan promosi?
2. Seberapa besar hubungan antara keterlambatan pengiriman (selisih antara tanggal pesanan diterima pelanggan dengan estimasi pengiriman) terhadap rata-rata skor ulasan pelanggan di berbagai negara bagian selama periode Januari 2017 hingga Agustus 2018, sehingga tim logistik dapat memprioritaskan perbaikan SLA pengiriman?

## Setup Environment - Anaconda
```bash
conda create --name main-ds python=3.9
conda activate main-ds
pip install -r requirements.txt
```

## Setup Environment - Shell/Terminal (venv)
1. Clone repositori dan masuk ke direktori proyek:
   ```bash
   git clone https://github.com/Xatria7/Submission-Fundamental-Analisis-Data.git
   cd Submission-Fundamental-Analisis-Data
   ```
2. Buat dan aktifkan virtual environment (`venv`):
   - **Windows (PowerShell/CMD):**
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```
   - **macOS / Linux:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
3. Instal seluruh pustaka (library) yang dibutuhkan:
   ```bash
   pip install -r requirements.txt
   ```

## Run Streamlit App
```bash
streamlit run Dashboard/dashboard.py
```