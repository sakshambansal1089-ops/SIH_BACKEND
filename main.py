from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import ParcelInput
import risk_model

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
    # Call Dev 2's ML prediction function directly
    return risk_model.predict_risk(data.model_dump())