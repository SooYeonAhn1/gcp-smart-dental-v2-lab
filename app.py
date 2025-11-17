from flask import Flask, request, jsonify
from flask_cors import CORS
from google.cloud import firestore
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

        services_list = data.get("services", [])
        has_service = any(service_num in service_item for service_item in services_list)

        if has_service:
            data["id"] = doc.id
            matching_results.append(data)

    return jsonify({
        "count": len(matching_results),
        "results": matching_results
    })


@app.route("/add-case-queue", methods=["POST"])
def add_case_queue():
    data = request.get_json()

    lab_id = data.get("lab_id")
    case_id = data.get("case_id")

    if not lab_id or not case_id:
        return jsonify({"error": "lab_id and case_id are required."}), 400
    
    doc_ref = db.collection("test-lab-data").document(str(lab_id))

    cur_availability = doc_ref.get().to_dict().get("availability", 0)
    cur_capacity = doc_ref.get().to_dict().get("capacity", 0)

    doc_ref.update({
        "queue": firestore.ArrayUnion([case_id]),
        "availability": max(0, ((cur_capacity - cur_availability) / cur_capacity) * 100)
    })

    cur_queue = doc_ref.get().to_dict().get("queue", [])

    return jsonify({
        "message": "case added to the queue",
        "lab_id": lab_id,
        "case_id": case_id,
        "current_queue": cur_queue,
        "capacity": cur_capacity,
        "cur_availability": doc_ref.get().to_dict().get("availability", 0)
    }), 200

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
