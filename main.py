import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from models import ParcelInput
import risk_model
import db

app = FastAPI(title="SIH 26017 - Land Acquisition Delay Backend")

# Enable CORS for Frontend Integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Google GenAI Client
ai_client = genai.Client()

@app.get("/")
def health_check():
    return {"status": "Online", "role": "Backend Engineer 3 - API & AI Engine"}

@app.get("/api/parcels")
def get_all_parcels():
    """Fetch all parcel records directly from MongoDB"""
    try:
        return db.get_all_parcels()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/parcels/{parcel_id}")
def get_parcel(parcel_id: str):
    """Fetch a specific parcel record by ID from MongoDB"""
    parcel = db.get_parcel_by_id(parcel_id)
    if not parcel:
        raise HTTPException(status_code=404, detail="Parcel not found")
    return parcel

@app.post("/api/parcels/assess-risk")
def assess_risk(data: ParcelInput):
    """Run Dev 2 ML risk prediction model & save to MongoDB"""
    assessment = risk_model.predict_risk(data.model_dump())
    
    try:
        db.save_prediction_result(assessment)
    except Exception as e:
        print(f"Database save non-critical warning: {e}")
        
    return assessment

@app.post("/api/parcels/mitigation-plan")
def generate_mitigation_plan(data: ParcelInput):
    """Generates an AI-driven delay mitigation plan via Google Gemini 3.6 Flash"""
    # 1. Obtain risk assessment from ML model
    risk_assessment = risk_model.predict_risk(data.model_dump())

    # 2. Build contextual prompt enforcing executive-level formal English
    prompt = f"""
You are an expert AI risk advisor specializing in Indian Infrastructure and Land Acquisition projects.
Provide a highly formal, executive-level, 3-step actionable mitigation plan in clear, standard English for this parcel delay risk.

CRITICAL LANGUAGE & TONE RULES:
1. Translate any informal, colloquial, or Hinglish risk factors into standard professional English.
2. Maintain a professional, executive, and authoritative tone suitable for high-level government or legal reports.
3. Do NOT use any Hinglish, informal phrases, or casual slang in your output under any circumstances.

Parcel Details:
Parcel ID: {data.parcel_id}
Project ID: {data.project_id}
District: {data.district}
Risk Level: {risk_assessment.get('risk_level', 'Unknown')}
Risk Score: {risk_assessment.get('risk_score', 0)}
Predicted Delay: {risk_assessment.get('predicted_delay_days', 0)} days
Primary Risk Factors: {', '.join(risk_assessment.get('primary_risk_factors', []))}

Focus on actionable steps to resolve legal stays, streamline disbursement/compensation, or address compensation issues.
"""

    # 3. Execute model call and handle DB persistence safely
    try:
        response = ai_client.models.generate_content(
            model='gemini-3.6-flash',
            contents=prompt,
        )

        result = {
            "parcel_id": data.parcel_id,
            "risk_summary": risk_assessment,
            "mitigation_plan": response.text
        }

        # Persist result to MongoDB
        try:
            db.save_prediction_result(result)
        except Exception as db_err:
            print(f"DB save warning: {db_err}")

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini AI Generation Error: {str(e)}")
