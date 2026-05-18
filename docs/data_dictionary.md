# Data Dictionary - MyFinance

## Dataset Utama

### 1. `myfinance_sprint1_master_dataset.csv`
Dataset master hasil data gathering, cleaning, labeling, feature engineering, dan filtering.

Jumlah baris: 12.429  
Jumlah kolom: 19

### 2. `myfinance_ai_training_dataset.csv`
Dataset final yang digunakan untuk kebutuhan training model auto-categorization.

Jumlah baris: 12.429  
Jumlah kolom: 8

## Data Dictionary

| Column Name | Data Type | Description | Role |
|---|---|---|---|
| source | string | Sumber data, seperti Alfagift, Tokopedia, additional, atau hasil scrape lainnya | Metadata |
| raw_category | string | Kategori asli dari sumber data sebelum distandarisasi | Raw feature |
| raw_subcategory | string | Subkategori asli dari sumber data | Raw feature |
| raw_category_refined | string | Kategori hasil refinement dari raw category dan raw subcategory | Intermediate feature |
| product_name_raw | string | Nama produk asli sebelum cleaning | Raw feature |
| product_clean | string | Nama produk setelah proses text cleaning dan normalisasi | Model feature |
| price | numeric | Harga produk/transaksi | Model/analysis feature |
| price_missing | boolean | Penanda apakah harga kosong | Data quality feature |
| has_price | boolean | Penanda apakah produk memiliki harga valid | Data quality feature |
| price_bin | categorical | Kelompok harga berdasarkan rentang tertentu | Engineered feature |
| name_length | integer | Panjang karakter nama produk | Engineered feature |
| word_count | integer | Jumlah kata pada nama produk | Engineered feature |
| contains_number | boolean | Penanda apakah nama produk mengandung angka | Engineered feature |
| size_value | numeric | Nilai ukuran produk jika terdeteksi, misalnya 250 dari 250 ml | Engineered feature |
| size_unit | string | Satuan ukuran produk, misalnya ml, g, kg, pcs | Engineered feature |
| Macro_Category | string | Kategori makro: NEEDS, WANTS, atau OTHERS | Target/label |
| Master_Category | string | Kategori utama final, misalnya Makan & Minum Harian | Target/label |
| label_confidence | string | Tingkat keyakinan hasil labeling | Metadata |
| is_ai_ready | boolean | Penanda apakah data siap digunakan untuk kebutuhan AI/modeling | Filter flag |

## Target Variable

Target utama untuk auto-categorization:

- `Master_Category`

Target level makro:

- `Macro_Category`

## Feature Columns

Fitur yang dapat digunakan untuk modeling:

- `product_clean`
- `price`
- `price_missing`
- `price_bin`
- `name_length`
- `word_count`
- `contains_number`
- `size_value`
- `size_unit`

## Columns Excluded from Training

Kolom berikut tidak digunakan sebagai fitur input karena berpotensi menyebabkan data leakage:

- `Master_Category`
- `Macro_Category`
- `label_confidence`
- `is_ai_ready`
- `raw_category_refined`, jika digunakan sebagai turunan langsung dari proses labeling

## Data Leakage Prevention

Untuk mencegah data leakage, kolom target seperti `Master_Category` dan `Macro_Category` tidak dimasukkan sebagai fitur input ketika model dilatih untuk memprediksi kategori. Kolom metadata atau kolom hasil labeling juga dipisahkan dari fitur utama.
