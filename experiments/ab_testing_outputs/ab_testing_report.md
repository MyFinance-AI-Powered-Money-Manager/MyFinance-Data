# A/B Testing Synthetic Report - MyFinance

## Context

A/B Testing ini menggunakan data sintetis untuk membandingkan dua flow input transaksi:

- Variant A: input kategori manual
- Variant B: input transaksi dengan bantuan AI auto-categorization

Catatan: Data ini adalah simulasi dan bukan data eksperimen pengguna nyata.

## Summary by Variant

| variant   |   users |   avg_completion_time_sec |   median_completion_time_sec |   completion_rate |   category_accuracy |   avg_num_corrections |   avg_satisfaction_score |
|:----------|--------:|--------------------------:|-----------------------------:|------------------:|--------------------:|----------------------:|-------------------------:|
| A         |      60 |                   96.1753 |                       97.2   |           93.3333 |             70      |              1.58333  |                  3.2     |
| B         |      60 |                   55.395  |                       54.885 |           98.3333 |             88.3333 |              0.683333 |                  3.91667 |

## Lift Analysis

| metric                |   variant_A |   variant_B |   difference_B_minus_A | interpretation   |
|:----------------------|------------:|------------:|-----------------------:|:-----------------|
| Completion time       |    96.1753  |   55.395    |             -40.7803   | Lower is better  |
| Completion rate       |    93.3333  |   98.3333   |               5        | Higher is better |
| Category accuracy     |    70       |   88.3333   |              18.3333   | Higher is better |
| Number of corrections |     1.58333 |    0.683333 |              -0.9      | Lower is better  |
| Satisfaction score    |     3.2     |    3.91667  |               0.716667 | Higher is better |

## Statistical Tests

| metric              | test            |   statistic |     p_value | significant_at_0.05   |
|:--------------------|:----------------|------------:|------------:|:----------------------|
| completion_time_sec | Welch t-test    |   17.7627   | 3.92687e-34 | True                  |
| num_corrections     | Welch t-test    |    4.40809  | 2.75596e-05 | True                  |
| satisfaction_score  | Welch t-test    |   -4.95069  | 2.57e-06    | True                  |
| transaction_saved   | Chi-square test |    0.834783 | 0.360893    | False                 |
| category_correct    | Chi-square test |    5.05263  | 0.0245886   | True                  |

## Decision

Rekomendasi: Variant B layak dipilih untuk flow utama karena secara simulasi lebih cepat, lebih akurat, membutuhkan koreksi lebih sedikit, dan memiliki satisfaction score lebih tinggi.

## Interpretation

Jika hasil ini digunakan dalam laporan teknis, tuliskan bahwa eksperimen ini merupakan simulasi untuk mendemonstrasikan metode evaluasi. Untuk validasi final, eksperimen perlu diulang menggunakan data pengguna nyata.
