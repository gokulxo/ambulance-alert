from flask import Flask, render_template, request, jsonify
import time
import math
import uuid
import os

app = Flask(__name__)

HOSPITALS = [
    {"lat": 13.0827, "lng": 80.2707, "name": "City General Hospital"},
    {"lat": 13.0569, "lng": 80.2091, "name": "Apollo Hospital"},
    {"lat": 13.0067, "lng": 80.2206, "name": "Fortis Malar Hospital"},
    {"lat": 13.1143, "lng": 80.2757, "name": "Stanley Medical Hospital"},
]

# Multiple trips storage - key is trip_id
trips = {}

def haversine_km(lat1, lng1, lat2, lng2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlng / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def find_nearest_hospital(lat, lng):
    nearest = None
    min_dist = float('inf')
    for h in HOSPITALS:
        d = haversine_km(lat, lng, h["lat"], h["lng"])
        if d < min_dist:
            min_dist = d
            nearest = h
    return nearest, min_dist

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ambulance')
def ambulance():
    return render_template('ambulance.html')

@app.route('/hospital')
def hospital():
    return render_template('hospital.html')


@app.route('/api/start_trip', methods=['POST'])
def start_trip():
    data = request.get_json()
    trip_id = str(uuid.uuid4())[:8]

    trips[trip_id] = {
        "trip_id": trip_id,
        "active": True,
        "patient_name": data.get("patient_name"),
        "age": data.get("age"),
        "condition": data.get("condition"),
        "lat": None,
        "lng": None,
        "status": "Ambulance Dispatched",
        "last_updated": time.time(),
        "nearest_hospital": None
    }

    return jsonify({"message": "Trip started", "trip_id": trip_id, "trip": trips[trip_id]})


@app.route('/api/update_location', methods=['POST'])
def update_location():
    data = request.get_json()
    trip_id = data.get("trip_id")
    lat = data.get("lat")
    lng = data.get("lng")

    if trip_id not in trips:
        return jsonify({"error": "Invalid trip_id"}), 404

    trips[trip_id]["lat"] = lat
    trips[trip_id]["lng"] = lng
    trips[trip_id]["status"] = "En Route"
    trips[trip_id]["last_updated"] = time.time()

    nearest, dist = find_nearest_hospital(lat, lng)
    trips[trip_id]["nearest_hospital"] = nearest

    return jsonify({"message": "Location updated", "nearest_hospital": nearest, "distance_km": dist})


@app.route('/api/get_all_trips', methods=['GET'])
def get_all_trips():
    active_trips = [t for t in trips.values() if t["active"]]
    return jsonify({"trips": active_trips})


@app.route('/api/end_trip', methods=['POST'])
def end_trip():
    data = request.get_json()
    trip_id = data.get("trip_id")

    if trip_id not in trips:
        return jsonify({"error": "Invalid trip_id"}), 404

    trips[trip_id]["active"] = False
    trips[trip_id]["status"] = "Arrived at Hospital"
    return jsonify({"message": "Trip ended"})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, port=port, host='0.0.0.0')
