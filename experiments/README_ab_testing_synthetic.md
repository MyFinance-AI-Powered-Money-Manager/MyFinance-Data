# A/B Testing Synthetic - MyFinance

Folder ini berisi implementasi A/B Testing menggunakan data sintetis untuk mendemonstrasikan metode evaluasi fitur **AI auto-categorization** pada MyFinance.

## Tujuan Eksperimen

Membandingkan dua flow input transaksi:

| Variant | Deskripsi |
|---|---|
| A | User melakukan input kategori secara manual |
| B | User dibantu AI auto-categorization |

## Metrik Evaluasi

| Metric | Tujuan |
|---|---|
| `completion_time_sec` | Mengukur waktu penyelesaian input transaksi. Lebih rendah lebih baik. |
| `transaction_saved` | Mengukur apakah transaksi berhasil disimpan. Lebih tinggi lebih baik. |
| `category_correct` | Mengukur apakah kategori yang dipilih benar. Lebih tinggi lebih baik. |
| `num_corrections` | Mengukur jumlah koreksi kategori/input. Lebih rendah lebih baik. |
| `satisfaction_score` | Mengukur kepuasan user skala 1-5. Lebih tinggi lebih baik. |

## Catatan Penting

Dataset ini adalah **data sintetis/simulasi**, bukan data eksperimen pengguna nyata.  
Gunakan sebagai bukti implementasi metode A/B Testing Python untuk Side Quest Data Science.

## Cara Menjalankan

```bash
python ab_testing_synthetic_myfinance.py
```

Output akan dibuat di folder:

```text
ab_testing_outputs/
```

## Output

```text
ab_testing_outputs/
├── synthetic_ab_testing_data.csv
├── ab_testing_summary_by_variant.csv
├── ab_testing_lift_analysis.csv
├── ab_testing_statistical_tests.csv
├── ab_testing_report.md
├── chart_avg_completion_time.png
├── chart_category_accuracy.png
├── chart_avg_num_corrections.png
└── chart_avg_satisfaction_score.png
```

## Kalimat untuk Laporan Teknis

A/B Testing dilakukan menggunakan data sintetis untuk mendemonstrasikan metode evaluasi fitur AI auto-categorization. Eksperimen membandingkan flow input kategori manual sebagai Variant A dengan flow input berbantuan AI sebagai Variant B. Metrik yang dievaluasi meliputi waktu penyelesaian, akurasi kategori, jumlah koreksi, tingkat keberhasilan penyimpanan transaksi, dan skor kepuasan. Karena data yang digunakan bersifat simulasi, hasil eksperimen tidak diklaim sebagai validasi pengguna nyata, tetapi digunakan sebagai bukti implementasi metode evaluasi dan rencana pengujian lanjutan.
