from pydantic import BaseModel
from typing import List
from datetime import date


class MonthlyVisitData(BaseModel):
    month: str
    visits: int


class QuarterlyVisitsResponseDTO(BaseModel):
    total_quarterly_visits: int
    average_daily_visits: float
    monthly_data: List[MonthlyVisitData]
    current_month_visits: int
    previous_month_visits: int
    growth_percentage: float 