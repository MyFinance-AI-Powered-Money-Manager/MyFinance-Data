# MyFinance Data Science

Repository ini berisi pipeline Data Science untuk proyek MyFinance, meliputi data gathering, data wrangling, EDA, feature engineering, dataset final, dashboard analitik, dan API pendukung fitur financial insight.

## Main Outputs

- Final master dataset: `final-datasets/myfinance_sprint1_master_dataset.csv`
- AI training dataset: `final-datasets/myfinance_ai_training_dataset.csv`
- EDA notebook: `final-datasets/data_wrangling_eda_all.ipynb`
- A/B Testing: `experiments/ab_testing_synthetic_myfinance.ipynb`
- Data Dictionary: `docs/data_dictionary.md`
- Technical Report: `docs/laporan_teknis_data_science.pdf`

## Data Science Features

1. Data wrangling and cleaning
2. Exploratory Data Analysis
3. Feature engineering
4. Financial Health Score
5. Budget usage analysis
6. Smart Money Leak Detection
7. Cashflow and overbudget risk prediction
8. Streamlit dashboard

## Setup Virtual Environment
### Setup Environment - Shell/Terminal
```
# Make sure you are in the project's directory
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Setup Environment - MacOS/Linux
```
# Make sure you are in the project's directory
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
```

### Setup Environment - Conda
```
# Make sure you are in the project's directory
conda create --name dashboard-environment python=3.11.99
conda activate dashboard-environment
pip install -r requirements.txt
```
