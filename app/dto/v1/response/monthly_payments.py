from pydantic import BaseModel
from typing import List
from datetime import date


class MonthlyPaymentData(BaseModel):
    month: str
    payments: float
    goal: float
    achievement_percentage: float


class MonthlyPaymentsResponseDTO(BaseModel):
    total_payments: float
    current_month_payments: float
    previous_month_payments: float
    monthly_data: List[MonthlyPaymentData]
    overall_goal_achievement: float 