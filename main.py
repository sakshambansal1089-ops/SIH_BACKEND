from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import ParcelInput
import risk_model
import db

app = FastAPI(title="SIH 26017 - Land Acquisition Delay Backend")

# Enable CORS for Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": "Online", "role": "Backend Engineer 3 - API & AI Engine"}

@app.get("/api/parcels")
def get_all_parcels():
    """Fetch all parcels from MongoDB database"""
    try:
        return db.get_all_parcels()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/parcels/{parcel_id}")
def get_parcel(parcel_id: str):
    """Fetch a single parcel by ID from MongoDB"""
    parcel = db.get_parcel_by_id(parcel_id)
    if not parcel:
        raise HTTPException(status_code=404, detail="Parcel not found")
    return parcel

@app.post("/api/parcels/assess-risk")
def assess_risk(data: ParcelInput):
    # 1. Run Dev 2's ML Prediction
    assessment = risk_model.predict_risk(data.model_dump())
    
    # 2. Persist prediction output into Dev 1's MongoDB database
    try:
        db.save_prediction_result(assessment)
    except Exception as e:
        # Continue and return response even if database save fails
        print(f"Database save error: {e}")
        
    return assessment