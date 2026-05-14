from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
import pandas as pd
import joblib

current_dir = Path(__file__).parent
df = pd.read_csv(current_dir / "df_features.csv")
df['actual_spend'] = df['transaction_count'] * df['avg_transaction_amount']

features = [
    'day_of_week', 'day_of_month', 'is_weekend', 'is_payday', 
    'is_month_start', 'is_month_end', 'amount_lag_1', 'amount_lag_7', 
    'rolling_mean_7', 'rolling_sum_7'
]

def makeModel(category: str):
    try:
        cat_df = df[df['master_category'] == category].sort_values('date').reset_index(drop=True)

        train_df = cat_df[cat_df['date'] < '2025-06-01'].dropna(subset=features + ['actual_spend'])
        X_train = train_df[features]
        y_train = train_df['actual_spend']

        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train) 

        joblib.dump(model, f'{current_dir}\category_model\{category} category model.joblib')
    except:
        print(f"{category} category doesn't exist")

categories = ['Hobi & Self-Reward','Jajan & Nongkrong', 'Kebutuhan Rumah & Mandi',
              'Lain-lain & Darurat', 'Makan & Minum Harian', 'Tagihan & Kewajiban',
              'Transportasi & Rutinitas']

for category in categories:
    makeModel(category=category)