import os
from dotenv import load_dotenv
from pymongo import MongoClient


# -----------------------------------
# LOAD ENVIRONMENT VARIABLES
# -----------------------------------

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")


# -----------------------------------
# CONNECT TO MONGODB
# -----------------------------------

def connect_to_database():
    """Connect to MongoDB Atlas and return the database."""

    if not MONGODB_URI:
        raise ValueError("MONGODB_URI not found in .env file")

    client = MongoClient(MONGODB_URI)

    # Test MongoDB connection
    client.admin.command("ping")

    database = client["land_acquisition_db"]

    return database


# -----------------------------------
# GET PARCEL BY ID
# -----------------------------------

def get_parcel_by_id(parcel_id):

    db = connect_to_database()

    parcels_collection = db["parcels"]

    parcel = parcels_collection.find_one(
        {"parcel_id": parcel_id},
        {"_id": 0}
    )

    return parcel


# -----------------------------------
# GET ALL PARCELS
# -----------------------------------

def get_all_parcels():

    db = connect_to_database()

    parcels_collection = db["parcels"]

    parcels = list(
        parcels_collection.find(
            {},
            {"_id": 0}
        )
    )

    return parcels


# -----------------------------------
# GET TRAINING DATA FOR ML ENGINEER
# -----------------------------------

def get_training_data():

    db = connect_to_database()

    parcels_collection = db["parcels"]

    training_data = list(
        parcels_collection.find(
            {},
            {"_id": 0}
        )
    )

    return training_data


# -----------------------------------
# SAVE PREDICTION RESULT
# -----------------------------------

def save_prediction_result(data):

    db = connect_to_database()

    predictions_collection = db["predictions"]

    result = predictions_collection.insert_one(data)

    return str(result.inserted_id)


# -----------------------------------
# TEST DATABASE FUNCTIONS
# -----------------------------------

if __name__ == "__main__":

    print("Testing MongoDB functions...\n")

    # Test 1: Get one parcel
    parcel = get_parcel_by_id("PARCEL0001")

    print("Parcel found:")
    print(parcel)

    # Test 2: Get all parcels
    parcels = get_all_parcels()

    print("\nTotal parcels:")
    print(len(parcels))

    # Test 3: Get ML training data
    training_data = get_training_data()

    print("\nML Training Records:")
    print(len(training_data))

    # Test 4: Save prediction result
    test_prediction = {
        "parcel_id": "PARCEL0001",
        "predicted_delay_days": 150,
        "risk_level": "High",
        "risk_score": 85
    }

    prediction_id = save_prediction_result(test_prediction)

    print("\nPrediction saved successfully!")
    print("Prediction ID:", prediction_id)