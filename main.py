from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import ParcelInput

app = FastAPI(title="SIH 26017 - Land Acquisition Delay Backend")

# Enable CORS so Frontend can connect without domain block errors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": "Online", "role": "Backend Engineer 3 - API & AI Engine"}

@app.post("/api/parcels/assess-risk")
def assess_risk(data: ParcelInput):
    # Rule-based calculation placeholder until Developer 2 provides ML model script
    base_risk = (data.litigation_cases_count * 25) + (100 - data.compensation_disbursed_pct) * 0.4
    if data.stay_order_active:
        base_risk += 20
        
    calculated_score = min(base_risk, 100.0)
    
    return {
        "parcel_id": data.parcel_id,
        "project_id": data.project_id,
        "district": data.district,
        "risk_score": round(calculated_score, 2),
        "risk_category": "High Risk" if calculated_score > 60 else "Low Risk",
        "predicted_delay_days": int(calculated_score * 2.5)
    }