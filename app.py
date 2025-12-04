from flask import Flask, request, jsonify
from flask_cors import CORS
from google.cloud import firestore, storage
from xgboost import Booster
import numpy as np
import pandas as pd
import xgboost as xgb
from datetime import datetime

# remove for gcp because it's not required
# from firebase_admin import firestore, credentials

# remove for gcp
# cred = credentials.Certificate("smart-bonus-293007-key.json")
# firebase_admin.initialize_app(cred, {
#     "projectId": "smart-bonus-293007"
# })

app = Flask(__name__)
CORS(app)
db = firestore.Client(database="clinic")

def load_model():
    storage_client = storage.Client()
    bucket_name = "dental-ai-pricing-model"
    bucket_pricing = storage_client.bucket(bucket_name)
    blob_pricing = bucket_pricing.blob("pricing_model.json")
    model_bytes = blob_pricing.download_as_bytes() 
    booster = Booster()
    booster.load_model(model_bytes)
    return booster

def predict_price(model, labs):
    
    now = datetime.now()
    curr_hour = now.hour
    curr_day = now.weekday()

    updated_results = []

    for lab in labs:
        services = lab.get("services_available", {})

        for service_id_str, service_info in services.items():
            
            base_price = service_info.get("price")
            hour_sin = np.sin(2 * np.pi * curr_hour / 24)
            hour_cos = np.cos(2 * np.pi * curr_hour / 24)
            dow_sin  = np.sin(2 * np.pi * curr_day / 7)
            dow_cos  = np.cos(2 * np.pi * curr_day / 7)

            row = {
                "lab_type": lab.get("type"),
                "service_id": int(service_id_str),
                "base_price": float(base_price),
                "hour": curr_hour,
                "day_of_week": curr_day,
                "hour_sin": hour_sin,
                "hour_cos": hour_cos,
                "dow_sin": dow_sin,
                "dow_cos": dow_cos
            }

            df_row = pd.DataFrame([row])
            dmatrix = xgb.DMatrix(df_row)

            multiplier = float(model.predict(dmatrix)[0])
            dynamic_price = float(base_price * multiplier)

            service_info["pred_multiplier"] = multiplier
            service_info["dynamic_price"] = dynamic_price

        updated_results.append(lab)

    return updated_results

@app.route("/search-service", methods=["GET"])
def search_service():

    lab_type = request.args.get("type", type=int)
    service_num = request.args.get("service")

    if lab_type is None or service_num is None:
        return jsonify({
            "error": "Missing required parameters: type and service"
        }), 400

    docs = db.collection("test-lab-data") \
             .where("type", "==", lab_type) \
             .stream()

    matching_results = []

    for doc in docs:
        data = doc.to_dict()
        services_available = data.get("services_available", {})
        has_service = service_num in services_available

        if has_service:
            data["id"] = doc.id
            matching_results.append(data)

    model = load_model()
    results_with_predictions = predict_price(model, matching_results)

    return jsonify({
        "count": len(results_with_predictions),
        "results": results_with_predictions
    })


@app.route("/add-case-queue", methods=["POST"])
def add_case_queue():
    data = request.get_json()

    lab_id = data.get("lab_id")
    case_id = data.get("case_id")
    service_type = data.get("service_type")

    if not lab_id or not case_id:
        return jsonify({"error": "lab_id and case_id are required."}), 400
    
    doc_ref = db.collection("test-lab-data").document(str(lab_id))

    doc_snapshot = doc_ref.get().to_dict()
    cur_capacity = doc_snapshot.get("capacity", 1)

    case_queue = doc_snapshot.get("case_queue", {})
    case_queue[case_id] = {
        "service_type": service_type
    }

    cur_queue_size = len(case_queue)
    availability = max(0, ((cur_capacity - cur_queue_size) / cur_capacity) * 100)

    doc_ref.update({
        "case_queue": case_queue,
        "availability": round(availability, 2)
    })

    return jsonify({
        "message": "case added to the queue",
        "lab_id": lab_id,
        "case_id": case_id,
        "current_queue": case_queue,
        "capacity": cur_capacity,
        "cur_availability": round(availability, 2)
    }), 200

# @app.route("/update-case-queue-tat", methods=["POST"])
# def update_case_queue():
#     data = request.get_json()

#     lab_id = data.get("lab_id")
#     case_id = data.get("case_id")
#     service_type = data.get("service_type")

#     if not lab_id or not case_id:
#         return jsonify({"error": "lab_id and case_id are required."}), 400
    
#     doc_ref = db.collection("test-lab-data").document(str(lab_id))
    
#     # to update availability
#     doc_snapshot = doc_ref.get().to_dict()
#     cur_capacity = doc_snapshot.get("capacity", 1)
#     cur_queue = doc_snapshot.get("queue", []) + [case_id]
#     cur_queue_size = len(cur_queue)
#     availability = max(0, ((cur_capacity - cur_queue_size) / cur_capacity) * 100)

#     # to update tat for the service
#     lab_services = doc_snapshot.get("services", [])
#     before_services = lab_services
#     for service in lab_services:
#         if service_type in service:
#             cur_tat = service[str(service_type)]["avg_tat"]
#             service[str(service_type)]["avg_tat"] =  cur_tat + (1 * (cur_tat * 0.05))

#     doc_ref.update({
#         "services": lab_services,
#         "queue": firestore.ArrayUnion([case_id]),
#         "availability": round(availability, 2)
#     })

#     return jsonify({
#         "message": "case added to the queue",
#         "lab_id": lab_id,
#         "case_id": case_id,
#         "current_queue": cur_queue,
#         "capacity": cur_capacity,
#         "services_befpre_update": before_services,
#         "services_after_update": lab_services,
#         "cur_availability": round(availability, 2)
#     }), 200

# for testing price retrieval
# @app.route("/price", methods=["GET"])
# def get_service_price():
#     lab_id = request.args.get("lab_id")
#     service_num = request.args.get("service")

#     if lab_id is None or service_num is None:
#         return jsonify({"error": "Missing parameters lab_id and service"}), 400

#     doc = db.collection("test-lab-data").document(lab_id).get()

#     if not doc.exists:
#         return jsonify({"error": "Lab ID not found"}), 404

#     data = doc.to_dict()
#     services_list = data.get("services", [])

#     def convert_tat(avg_tat):
#         days = int(avg_tat)
#         decimal = avg_tat - days
#         hours_float = decimal * 24
#         hours = int(hours_float)
#         minutes = int((hours_float - hours) * 60)
#         return {"days": days, "hours": hours, "minutes": minutes}

#     for service_item in services_list:
#         if service_num in service_item:
#             info = service_item[service_num]
#             tat_raw = info["avg_tat"]
#             tat_converted = convert_tat(tat_raw)

#             return jsonify({
#                 "lab_id": lab_id,
#                 "service": service_num,
#                 "price": info["price"],
#                 "avg_tat_days": tat_raw,
#                 "converted_tat": tat_converted
#             })

#     return jsonify({"error": "Service not found for this lab"}), 404



@app.route("/")
def home():
    return {"message": "Service matching API running!"}


if __name__ == "__main__":
    app.run(port=8000, debug=True)
