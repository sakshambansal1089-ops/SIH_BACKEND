import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google import genai

app = FastAPI(title="Land Acquisition & Mitigation API")

# Initialize Google GenAI Client (requires GEMINI_API_KEY environment variable on Render)
ai_client = genai.Client()

# Request Body Schema
class ParcelInput(BaseModel):
    project_id: str
    parcel_id: str
    district: str
    litigation_cases_count: int
    stay_order_active: bool
    compensation_disbursed_pct: float


@app.get("/")
def read_root():
    return {"status": "online", "message": "SIH Backend API is running."}


@app.post("/api/parcels/mitigation-plan")
def generate_mitigation_plan(data: ParcelInput):
    """
    Generates an AI-driven delay mitigation plan via Google Gemini 3.6 Flash
    """
    # 1. Safely execute ML Risk Prediction
    try:
        # If risk_model is imported from your internal module
        risk_assessment = risk_model.predict_risk(data.model_dump())
    except Exception as ml_err:
        # Fallback dictionary if risk_model fails or is not initialized
        risk_assessment = {
            "risk_level": "High" if data.stay_order_active else "Medium",
            "risk_score": 75 if data.stay_order_active else 45,
            "predicted_delay_days": 180 if data.stay_order_active else 60,
            "primary_risk_factors": ["Pending Litigation", "Active Stay Order"] if data.stay_order_active else ["Compensation Pending"]
        }
        print(f"ML Model Warning (using fallback): {ml_err}")

    # 2. Build contextual prompt enforcing executive formal English
  # 2. Build contextual prompt enforcing executive formal English and word limit
    prompt = f"""
You are an expert AI risk advisor specializing in Indian Infrastructure and Land Acquisition projects.
Provide a highly formal, executive-level, 3-step actionable mitigation plan in clear, standard English for this parcel delay risk.

CRITICAL CONSTRAINTS & TONE RULES:
1. WORD LIMIT: Keep the ENTIRE mitigation plan concise and strictly under 150 words.
2. Translate any informal, colloquial, or Hinglish risk factors into standard professional English.
3. Maintain a professional, executive, and authoritative tone suitable for high-level government or legal reports.
4. Do NOT use any Hinglish, informal phrases, or casual slang in your output under any circumstances.

Parcel Details:
Parcel ID: {data.parcel_id}
Project ID: {data.project_id}
District: {data.district}
Risk Level: {risk_assessment.get('risk_level', 'Unknown')}
Risk Score: {risk_assessment.get('risk_score', 0)}
Predicted Delay: {risk_assessment.get('predicted_delay_days', 0)} days
Primary Risk Factors: {', '.join(risk_assessment.get('primary_risk_factors', []))}

Focus on brief, high-impact actionable steps to resolve legal stays and streamline compensation.
"""
    # 3. Call Gemini 3.6 Flash safely
    try:
        response = ai_client.models.generate_content(
            model='gemini-3.6-flash',
            contents=prompt,
        )
        mitigation_text = response.text
    except Exception as ai_err:
        raise HTTPException(
            status_code=500, 
            detail=f"Gemini API Call Failed: {str(ai_err)}"
        )

    result = {
        "parcel_id": data.parcel_id,
        "risk_summary": risk_assessment,
        "mitigation_plan": mitigation_text
    }

    # 4. Safely persist to database
    try:
        db.save_prediction_result(result)
    except Exception as db_err:
        print(f"Database Persistence Warning: {db_err}")

    return result
