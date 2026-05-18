from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from datetime import date
import pandas as pd

def makeModel(df, category: str, current_date):
    today = current_date
    first_of_month = today.replace(day=1)
    features = [
    'day_of_week', 'day_of_month', 'is_weekend', 'is_payday', 
    'is_month_start', 'is_month_end', 'amount_lag_1', 'amount_lag_7', 
    'rolling_mean_7', 'rolling_sum_7'
    ]
    try:
        cat_df = df[df['subcategory'] == category].sort_values('date').reset_index(drop=True)
        train_df = cat_df[cat_df['date'] < first_of_month].dropna(subset=features + ['actual_spend'])
        X_train = train_df[features]
        y_train = train_df['actual_spend']

        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train) 

        return model
    except Exception as e:
        return e

def predict(current_data, model, current_date):
    end_of_month = current_date + pd.offsets.MonthEnd(0)
    predictions = []
    history = current_data[['date', 'actual_spend']].copy()
    dates_to_predict = pd.date_range(start=current_date, end=end_of_month)

    # Making dataframe for the prediction
    for current_date in dates_to_predict:
        dow = current_date.dayofweek
        dom = current_date.day
        is_weekend = 1 if dow >= 5 else 0
        is_payday = 1 if dom in [25, 26, 27, 28] else 0 
        is_month_start = 1 if dom == 1 else 0
        is_month_end = 1 if current_date.is_month_end else 0
        
        last_1_val = history.iloc[-1]['actual_spend']
        last_7_val = history.iloc[-7]['actual_spend'] if len(history) >= 7 else 0
        
        last_7_days = history.tail(7)['actual_spend']
        roll_mean = last_7_days.mean()
        roll_sum = last_7_days.sum()
        
        X_pred = pd.DataFrame([{
            'day_of_week': dow,
            'day_of_month': dom,
            'is_weekend': is_weekend,
            'is_payday': is_payday,
            'is_month_start': is_month_start,
            'is_month_end': is_month_end,
            'amount_lag_1': last_1_val,
            'amount_lag_7': last_7_val,
            'rolling_mean_7': roll_mean,
            'rolling_sum_7': roll_sum
        }])

        # Predict the spending of current_date
        pred_spend = model.predict(X_pred)[0]
        predictions.append({'date': current_date, 'predicted_spend': pred_spend})
        
        # Predict using past data
        new_row = pd.DataFrame({'date': [current_date], 'actual_spend': [pred_spend]})
        history = pd.concat([history, new_row]).reset_index(drop=True)

    pred_df = pd.DataFrame(predictions)
    total_predicted = pred_df['predicted_spend'].sum()
    current_actual = current_data['actual_spend'].values[0]
    total_month_forecast = current_actual + total_predicted

    return total_month_forecast

def predict_categories(df):
    categories = ['Hobi & Self-Reward','Jajan & Nongkrong', 'Kebutuhan Rumah & Mandi',
              'Lain-lain & Darurat', 'Makan & Minum Harian', 'Tagihan & Kewajiban',
              'Transportasi & Rutinitas']
    try:
        cat_df = df[df['subcategory'] == category].sort_values('date').reset_index(drop=True)
    except:
        df = df.rename(columns={
            'master_category': 'subcategory'
        })
    
    df['actual_spend'] = df['transaction_count'] * df['avg_transaction_amount']
    current_date = pd.Timestamp.now()
    result = {}
    for category in categories:
        model = makeModel(df, category=category, current_date=current_date)
        cat_df = df[df['subcategory'] == category].sort_values('date').reset_index(drop=True)
        current_data = cat_df[cat_df['date'] <= current_date][['date', 'actual_spend']]
        result[category] = predict(current_data, model, current_date)
        # print(f'prediction for {category}: {predict(current_data, model, current_date)}')
    result['total'] = sum(result.values())
    return result

def to_features(df):
    # DATA CLEANING

    df_clean = df.copy()

    required_columns = ["timestamp", "type", "amount", "master_category"]

    missing_columns = [col for col in required_columns if col not in df_clean.columns]

    if missing_columns:
        raise ValueError(f"Kolom wajib tidak ditemukan: {missing_columns}")

    # Convert tipe data
    df_clean["timestamp"] = pd.to_datetime(df_clean["timestamp"], errors="coerce").dt.tz_localize(None)
    df_clean["amount"] = pd.to_numeric(df_clean["amount"], errors="coerce")

    # Drop data kosong pada kolom penting
    df_clean = df_clean.dropna(subset=["timestamp", "type", "amount", "master_category"])

    # Amount dibuat positif
    df_clean["amount"] = df_clean["amount"].abs()

    # Buat kolom tanggal
    df_clean["date"] = df_clean["timestamp"].dt.normalize()

    # Jika macro_category tidak ada, buat default Unknown
    if "macro_category" not in df_clean.columns:
        df_clean["macro_category"] = "Unknown"
    else:
        df_clean["macro_category"] = df_clean["macro_category"].fillna("Unknown")

    # Jika title tidak ada, pakai master_category sebagai title
    if "title" not in df_clean.columns:
        df_clean["title"] = df_clean["master_category"]
    else:
        df_clean["title"] = df_clean["title"].fillna(df_clean["master_category"])

    # Pisahkan income dan expense
    df_expense = df_clean[df_clean["type"].str.lower() == "expense"].copy()
    df_income = df_clean[df_clean["type"].str.lower() != "expense"].copy()

    # CASHFLOW & OVERBUDGET FEATURE ENGINEERING

    # Agregasi harian per master_category
    df_daily = (
        df_expense
        .groupby(["date", "master_category"], as_index=False)
        .agg(
            target_daily_category_amount=("amount", "sum"),
            transaction_count=("amount", "count"),
            avg_transaction_amount=("amount", "mean")
        )
    )

    # Full grid tanggal x kategori
    all_dates = pd.date_range(
        start=df_expense["date"].min(),
        end=df_expense["date"].max(),
        freq="D"
    )

    all_categories = sorted(df_expense["master_category"].unique())

    full_grid = pd.MultiIndex.from_product(
        [all_dates, all_categories],
        names=["date", "master_category"]
    ).to_frame(index=False)

    df_features = full_grid.merge(
        df_daily,
        on=["date", "master_category"],
        how="left"
    )

    # Hari tanpa transaksi diisi 0
    fill_zero_cols = [
        "target_daily_category_amount",
        "transaction_count",
        "avg_transaction_amount"
    ]

    df_features[fill_zero_cols] = df_features[fill_zero_cols].fillna(0)

    # Sort
    df_features = df_features.sort_values(["master_category", "date"]).reset_index(drop=True)

    # Time features
    df_features["day_of_week"] = df_features["date"].dt.dayofweek
    df_features["day_of_month"] = df_features["date"].dt.day
    df_features["month"] = df_features["date"].dt.month
    df_features["year"] = df_features["date"].dt.year
    df_features["week_of_year"] = df_features["date"].dt.isocalendar().week.astype(int)
    df_features["year_month"] = df_features["date"].dt.to_period("M").astype(str)

    df_features["is_weekend"] = df_features["day_of_week"].isin([5, 6]).astype(int)
    df_features["is_payday"] = df_features["day_of_month"].isin([1, 2, 3]).astype(int)
    df_features["is_month_start"] = df_features["date"].dt.is_month_start.astype(int)
    df_features["is_month_end"] = df_features["date"].dt.is_month_end.astype(int)

    df_features["days_until_month_end"] = (
        df_features["date"].dt.days_in_month - df_features["day_of_month"]
    )

    target_col = "target_daily_category_amount"

    # Lag features
    df_features["amount_lag_1"] = (
        df_features.groupby("master_category")[target_col].shift(1)
    )

    df_features["amount_lag_7"] = (
        df_features.groupby("master_category")[target_col].shift(7)
    )

    # Rolling features, pakai shift(1) supaya tidak leakage
    df_features["rolling_mean_7"] = (
        df_features
        .groupby("master_category")[target_col]
        .transform(lambda x: x.shift(1).rolling(7, min_periods=1).mean())
    )

    df_features["rolling_sum_7"] = (
        df_features
        .groupby("master_category")[target_col]
        .transform(lambda x: x.shift(1).rolling(7, min_periods=1).sum())
    )

    df_features["rolling_mean_14"] = (
        df_features
        .groupby("master_category")[target_col]
        .transform(lambda x: x.shift(1).rolling(14, min_periods=1).mean())
    )

    df_features["rolling_sum_30"] = (
        df_features
        .groupby("master_category")[target_col]
        .transform(lambda x: x.shift(1).rolling(30, min_periods=1).sum())
    )

    # Month-to-date sebelum hari ini
    df_features["month_to_date_amount_before_today"] = (
        df_features
        .groupby(["master_category", "year_month"])[target_col]
        .transform(lambda x: x.shift(1).cumsum())
    )

    feature_fill_cols = [
        "amount_lag_1",
        "amount_lag_7",
        "rolling_mean_7",
        "rolling_sum_7",
        "rolling_mean_14",
        "rolling_sum_30",
        "month_to_date_amount_before_today"
    ]

    df_features[feature_fill_cols] = df_features[feature_fill_cols].fillna(0)

    # Total harian semua kategori
    daily_total = (
        df_features
        .groupby("date", as_index=False)[target_col]
        .sum()
        .rename(columns={target_col: "daily_total_amount"})
    )

    df_features = df_features.merge(daily_total, on="date", how="left")

    return df_features