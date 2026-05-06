from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Literal, Dict

app = FastAPI(title="Data Processing API")

# Input Structure
class Transaction(BaseModel):
    type: Literal["INCOME", "EXPENSE"]
    amount: float
    category: Literal["NEEDS", "WANTS"]
    subcategory: str
    transaction_date: str

class BudgetLimit(BaseModel):
    subcategory: str
    limit: float

class MonthlyDataRequest(BaseModel):
    budgets: List[BudgetLimit]
    transactions: List[Transaction]

# Output Structure
class CategorySummary(BaseModel):
    subcategory: str
    limit: float
    spent: float
    remaining: float
    percentage_used: float

class MonthlySummaryResponse(BaseModel):
    categories: List[CategorySummary]
    total_spent: float
    total_budget: float

# Endpoint
@app.post("/api/v1/calculate-budget", response_model=MonthlySummaryResponse)
async def calculate_monthly_budget(payload: MonthlyDataRequest):
    # Calculate total spent per subcategory
    spent_dict: Dict[str, float] = {}
    
    for transaction in payload.transactions:
        if transaction.type == "EXPENSE":
            # Add to existing amount or initialize at 0
            spent_dict[transaction.subcategory] = spent_dict.get(transaction.subcategory, 0.0) + transaction.amount

    # Compare against budgets and calculate metrics
    results = []
    total_spent_overall = 0.0
    total_budget_overall = 0.0

    for budget in payload.budgets:
        spent = spent_dict.get(budget.subcategory, 0.0)
        remaining = budget.limit - spent
        
        if budget.limit > 0:
            percentage_used = (spent / budget.limit) * 100
        else:
            percentage_used = 0.0

        results.append(CategorySummary(
            subcategory=budget.subcategory,
            limit=budget.limit,
            spent=spent,
            remaining=remaining,
            percentage_used=round(percentage_used, 2)
        ))

        total_spent_overall += spent
        total_budget_overall += budget.limit

    return MonthlySummaryResponse(
        categories=results,
        total_spent=total_spent_overall,
        total_budget=total_budget_overall
    )

"""
Example of JSON  Input
{
  "budgets": [
    {
      "subcategory": "Makan & Minum Harian",
      "limit": 1500000
    },
    {
      "subcategory": "Transportasi & Rutinitas",
      "limit": 500000
    }
  ],
  "transactions": [
    {
      "type": "EXPENSE",
      "amount": 23200,
      "category": "NEEDS",
      "subcategory": "Makan & Minum Harian",
      "transaction_date": "2026-05-06"
    },
    {
      "type": "EXPENSE",
      "amount": 50000,
      "category": "NEEDS",
      "subcategory": "Makan & Minum Harian",
      "transaction_date": "2026-05-06"
    },
    {
      "type": "EXPENSE",
      "amount": 9600,
      "category": "NEEDS",
      "subcategory": "Transportasi & Rutinitas",
      "transaction_date": "2026-05-06"
    },
    {
      "type": "INCOME",
      "amount": 4627415,
      "category": "NEEDS",
      "subcategory": "Salary",
      "transaction_date": "2026-05-06"
    }
  ]
}
"""

class Transaction(BaseModel):
    type: Literal["INCOME", "EXPENSE"]
    amount: float
    category: Literal["NEEDS", "WANTS"]
    subcategory: str
    transaction_date: str