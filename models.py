from pydantic import BaseModel

class ParcelInput(BaseModel):
    project_id: str
    parcel_id: str
    district: str
    litigation_cases_count: int
    stay_order_active: bool
    compensation_disbursed_pct: float