from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import pandas as pd
import json

class Transaction(BaseModel):
    id: str
    wallet_id: str
    type: str
    total_amount: int
    category: str
    subcategory: str
    description: str
    transaction_date: str

class TransactionItem(BaseModel):
    id: str
    transaction_id: str
    item_name: str
    price: int
    category: str
    subcategory: str

class Budget(BaseModel):
    id: str
    category: str
    limit_amount: int
    month_period: str

class FinancialPayload(BaseModel):
    user_id: str
    month_period: str
    transactions: List[Transaction]
    transaction_items: List[TransactionItem]
    budgets: List[Budget]

def to_dataframe(payload: FinancialPayload, type) -> dict:
    try:
        # Turn JSON payload into a format pandas can read with pydantic
        transactions_data = [t.model_dump() for t in payload.transactions]
        items_data = [i.model_dump() for i in payload.transaction_items]
        budgets_data = [b.model_dump() for b in payload.budgets]
        
        # Create dataframe
        df_transactions = pd.DataFrame(transactions_data)
        df_items = pd.DataFrame(items_data)
        df_budgets = pd.DataFrame(budgets_data)
        
        if type == 'df_joined':
            df_items.drop(columns=['id'], inplace=True)
            df_items.rename(columns={'transaction_id': 'id'}, inplace=True)
            print(df_items)
            print('columns: \n', df_items.columns)
            print('---------------------')
            print(df_transactions)
            print('columns: \n', df_transactions.columns)

            df_joined = pd.merge(
            df_items, 
            df_transactions[['id', 'type', 'transaction_date']], 
            left_on='id', 
            right_on='id', 
            how='inner'
            )

            df_joined.drop(columns=['id'], inplace=True)
            df_joined.rename(columns=
                            {
                                'transaction_date': 'timestamp',
                                'item_name': 'title',
                                'subcategory': 'master_category',
                                'category': 'macro_category',
                                'price': 'amount',
                            }, inplace=True)
            
            return df_joined
        elif type == 'df_transactions':
            return df_transactions
        elif type == 'df_items':
            return df_items
        elif type == 'df_budgets':
            return df_budgets
        else:
            raise ValueError("Please input the second parameter as df_joined, df_transactions, df_items, or df_budgets")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing data: {str(e)}")
    
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