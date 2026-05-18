from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from utils import to_dataframe
from category_prediction import to_features, predict_categories
from calculate_budget_v2 import calculate_monthly_budget
from leak_detection_and_financial_score_training import leak_and_financial_score
import pandas as pd

app = FastAPI(title="Data Processing API")

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

# Endpoints
@app.post("/category-prediction/")
async def category_prediction(payload: FinancialPayload):
    try:
      df = to_dataframe(payload, 'df_joined')
      feature_ready_df = to_features(df)
      predicted_categories = predict_categories(feature_ready_df)
      return predicted_categories
    
    except Exception as e:
        return f"Error: {e}"
@app.post('/budget-calculator/')
async def budget_calculator(payload: FinancialPayload):
    try:
        result = calculate_monthly_budget(payload.model_dump())
        return {"budgets": result}
    except Exception as e:
        return f"error: {e}"
    
@app.post("/leak-detection-and-financial-score")
async def leak_and_score(payload: FinancialPayload):
    try:
        df = to_dataframe(payload, 'df_joined')
        summary = leak_and_financial_score(df)
        return summary
    except Exception as e:
        return f"error: {e}"