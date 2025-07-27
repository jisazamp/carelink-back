from pydantic import BaseModel
from typing import List
from datetime import date


class MonthlyEfficiencyData(BaseModel):
    month: str
    efficiency: float
    attendance_rate: float
    home_visits_completion: float
    contract_management: float
    billing_efficiency: float


class OperationalEfficiencyResponseDTO(BaseModel):
    overall_efficiency: float
    current_month_efficiency: float
    previous_month_efficiency: float
    monthly_data: List[MonthlyEfficiencyData]
    attendance_rate: float
    home_visits_completion_rate: float
    contract_management_rate: float
    billing_efficiency_rate: float
    growth_percentage: float 