# E-Commerce Public Dataset Analytics Dashboard

Proyek akhir Analisis Data menggunakan **E-Commerce Public Dataset** yang mencakup eksplorasi data, analisis perilaku pelanggan (RFM Analysis), serta dashboard interaktif berbasis Streamlit.

**Live Dashboard:** [https://dashboard-satria.streamlit.app](https://dashboard-satria.streamlit.app)

## Struktur Direktori
```text
├── Dashboard/
│   ├── dashboard.py
│   └── main_data.csv
├── data/
│   └── (9 file dataset mentah .csv)
├── notebook_SatriaDCF.ipynb
├── README.md
├── requirements.txt
└── url.txt
```

## Pertanyaan Bisnis
1. Bagaimana tren pertumbuhan jumlah pesanan dan total pendapatan (*revenue*) bulanan pada periode Januari 2017 hingga Agustus 2018, serta 10 kategori produk apa saja yang menghasilkan pendapatan tertinggi dan terendah?
2. Seberapa besar dampak keterlambatan pengiriman (selisih antara tanggal pesanan diterima pelanggan dengan estimasi pengiriman) terhadap penurunan rata-rata skor ulasan pelanggan (*review score*) di seluruh negara bagian (*customer state*) selama periode 2017–2018?

## Cara Menjalankan Dashboard secara Lokal
1. Clone repositori ini:
   ```bash
   git clone [https://github.com/Xatria7/Submission-Fundamental-Analisis-Data.git](https://github.com/Xatria7/Submission-Fundamental-Analisis-Data.git)
   cd Submission-Fundamental-Analisis-Data
   ```
2. Instal seluruh dependensi yang diperlukan:
   ```bash
   pip install -r requirements.txt
   ```
3. Jalankan aplikasi Streamlit:
   ```bash
   streamlit run Dashboard/dashboard.py
   ```