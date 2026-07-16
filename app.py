from flask import Flask, render_template, request, jsonify
import time
import math

app = Flask(__name__)

# Multiple hospitals list (demo ku - Chennai example locations, un area ku change pannikonga)
HOSPITALS = [
    {"lat": 13.0827, "lng": 80.2707, "name": "City General Hospital"},
    {"lat": 13.0569, "lng": 80.2091, "name": "Apollo Hospital"},
    {"lat": 13.0067, "lng": 80.2206, "name": "Fortis Malar Hospital"},
    {"lat": 13.1143, "lng": 80.2757, "name": "Stanley Medical Hospital"},
]

# In-memory storage (hackathon demo ku DB venaam)
trip_data = {
    "active": False,
    "patient_name": "",
    "age": "",
    "condition": "",
    "lat": None,
    "lng": None,
    "status": "No active trip",
    "last_updated": None,
    "nearest_hospital": None
}

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


# ---- API ROUTES ----

@app.route('/api/start_trip', methods=['POST'])
def start_trip():
    data = request.get_json()
    trip_data["active"] = True
    trip_data["patient_name"] = data.get("patient_name")
    trip_data["age"] = data.get("age")
    trip_data["condition"] = data.get("condition")
    trip_data["status"] = "Ambulance Dispatched"
    trip_data["last_updated"] = time.time()
    trip_data["nearest_hospital"] = None
    return jsonify({"message": "Trip started", "trip": trip_data})


@app.route('/api/update_location', methods=['POST'])
def update_location():
    data = request.get_json()
    lat = data.get("lat")
    lng = data.get("lng")
    trip_data["lat"] = lat
    trip_data["lng"] = lng
    trip_data["status"] = "En Route"
    trip_data["last_updated"] = time.time()

    nearest, dist = find_nearest_hospital(lat, lng)
    trip_data["nearest_hospital"] = nearest

    return jsonify({"message": "Location updated", "nearest_hospital": nearest, "distance_km": dist})


@app.route('/api/get_latest', methods=['GET'])
def get_latest():
    response = dict(trip_data)
    return jsonify(response)


@app.route('/api/end_trip', methods=['POST'])
def end_trip():
    trip_data["active"] = False
    trip_data["status"] = "Arrived at Hospital"
    return jsonify({"message": "Trip ended"})


if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
