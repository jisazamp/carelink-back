from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import date


class MonthlyVisitData(BaseModel):
    month: str
    visits: int


class ProfessionalVisitData(BaseModel):
    id_profesional: int
    visit_count: int


class QuarterlyVisitsResponseDTO(BaseModel):
    total_quarterly_visits: int
    average_daily_visits: float
    monthly_data: List[MonthlyVisitData]
    current_month_visits: int
    previous_month_visits: int
    growth_percentage: float
    visits_by_status: Dict[str, int]
    active_professionals: List[ProfessionalVisitData]
    completed_visits: int
    pending_visits: int
    cancelled_visits: int
    rescheduled_visits: int
    completion_rate: float
    efficiency_rate: float 