import joblib
import os

def calculate_weighted_score(data):
    lit = data.get('litigation_cases_count', 0)
    stay = data.get('stay_order_active', False)
    comp = data.get('compensation_disbursed_pct', 100)

    litigation_score = min(lit * 15, 50)
    stay_score = 40 if stay else 0
    comp_score = (100 - comp) * 0.3

    total = litigation_score + stay_score + comp_score
    return min(total, 100)

# Model load karo
try:
    ml_model = joblib.load(os.path.join(os.path.dirname(__file__), "model.pkl"))
except:
    ml_model = None

def predict_risk(parcel_data: dict):
    score = calculate_weighted_score(parcel_data)

    if ml_model:
        features = [[
            parcel_data.get('litigation_cases_count', 0),
            1 if parcel_data.get('stay_order_active') else 0,
            parcel_data.get('compensation_disbursed_pct', 0)
        ]]
        delay = int(ml_model.predict(features)[0])
    else:
        delay = int(score * 2.5)

    if score > 70:
        level = "High"
    elif score > 40:
        level = "Medium"
    else:
        level = "Low"

    factors = []
    if parcel_data.get('litigation_cases_count', 0) > 0:
        factors.append(f"{parcel_data['litigation_cases_count']} case chal rahe hai")
    if parcel_data.get('stay_order_active'):
        factors.append("Court ka Stay Order laga hai")
    if parcel_data.get('compensation_disbursed_pct', 100) < 80:
        factors.append(f"Sirf {parcel_data.get('compensation_disbursed_pct')}% paisa diya hai")
    if not factors:
        factors.append("Sab clear hai - koi risk nahi")

    return {
        "parcel_id": parcel_data.get("parcel_id"),
        "risk_score": round(score, 2),
        "risk_level": level,
        "predicted_delay_days": delay,
        "primary_risk_factors": factors
    }