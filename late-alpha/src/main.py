from flask import Flask, jsonify, request, render_template # type: ignore
import random
import json
import os
import math

app = Flask(__name__, static_folder='static', template_folder='templates')

# Data persistence files
FLIGHTS_FILE = 'flights.json'
FLIGHT_PLANS_FILE = 'flight_plans.json'

# Aircraft types
aircraft_types = [
    "Boeing 737-800", "Boeing 737 MAX-8", "Boeing 737 MAX-9",
    "Airbus A319", "Airbus A319neo", "Airbus A320", "Airbus A320neo",
    "Airbus A321", "Airbus A321neo", "Airbus A321XLR", "Airbus A330",
    "Boeing 757", "Boeing 767", "Boeing 777", "Boeing 787", "Airbus A350"
]

# US waypoints/VORs
waypoints = [
    "ATL", "BOS", "ORD", "DFW", "DEN", "SEA", "SFO", "LAX", "PHX", "LAS",
    "MSP", "DTW", "CLE", "PIT", "BWI", "IAD", "CLT", "RDU", "BNA", "MEM",
    "STL", "CVG", "IND", "CMH", "SDF", "MSY", "HOU", "SAT", "AUS", "ELP",
    "ABQ", "OKC", "TUL", "DSM", "OMA", "ICT", "MCI", "SLC", "BOI", "GEG", "PDX"
]

# Airport coordinates (lat, lon)
airport_coords = {
    "JFK": (40.6413, -73.7781),
    "LAX": (33.9425, -118.4081),
    "ATL": (33.6407, -84.4277),
    "ORD": (41.9742, -87.9073),
    "DFW": (32.8998, -97.0403),
    "DEN": (39.8561, -104.6737),
    "SEA": (47.4502, -122.3088),
    "SFO": (37.6189, -122.3750),
    "PHX": (33.4343, -112.0116),
    "LAS": (36.0840, -115.1537),
    "MSP": (44.8848, -93.2223),
    "DTW": (42.2124, -83.3534),
    "CLE": (41.4094, -81.8547),
    "PIT": (40.4915, -80.2327),
    "BWI": (39.1754, -76.6683),
    "IAD": (38.9445, -77.4558),
    "CLT": (35.2140, -80.9431),
    "RDU": (35.8776, -78.7875),
    "BNA": (36.1245, -86.6782),
    "MEM": (35.0421, -89.9792),
    "STL": (38.7487, -90.3700),
    "CVG": (39.0488, -84.6678),
    "IND": (39.7173, -86.2944),
    "CMH": (39.9980, -82.8919),
    "SDF": (38.1744, -85.7360),
    "MSY": (29.9934, -90.2580),
    "HOU": (29.6454, -95.2789),
    "SAT": (29.5337, -98.4698),
    "AUS": (30.1945, -97.6699),
    "ELP": (31.8072, -106.3776),
    "ABQ": (35.0402, -106.6090),
    "OKC": (35.3931, -97.6007),
    "TUL": (36.1984, -95.8881),
    "DSM": (41.5340, -93.6631),
    "OMA": (41.3032, -95.8941),
    "ICT": (37.6499, -97.4331),
    "MCI": (39.2976, -94.7139),
    "SLC": (40.7884, -111.9778),
    "BOI": (43.5644, -114.3430),
    "GEG": (47.6191, -117.5336),
    "PDX": (45.5887, -122.5968),
}

vor_coords = airport_coords  # Approximate VOR coords to airport coords

# Aircraft specs: speed (km/h), burn (kg/h)
aircraft_specs = {
    "Boeing 737-800": {"speed": 850, "burn": 4250},  # Increased burn for realistic fuel
    "Boeing 737 MAX-8": {"speed": 850, "burn": 4250},
    "Boeing 737 MAX-9": {"speed": 850, "burn": 4250},
    "Airbus A319": {"speed": 830, "burn": 3750},
    "Airbus A319neo": {"speed": 830, "burn": 3500},
    "Airbus A320": {"speed": 830, "burn": 4000},
    "Airbus A320neo": {"speed": 830, "burn": 3750},
    "Airbus A321": {"speed": 830, "burn": 4250},
    "Airbus A321neo": {"speed": 830, "burn": 4000},
    "Airbus A321XLR": {"speed": 830, "burn": 4000},
    "Airbus A330": {"speed": 870, "burn": 12500},
    "Boeing 757": {"speed": 850, "burn": 6000},
    "Boeing 767": {"speed": 850, "burn": 10000},
    "Boeing 777": {"speed": 890, "burn": 17500},
    "Boeing 787": {"speed": 900, "burn": 12500},
    "Airbus A350": {"speed": 900, "burn": 14000},
}
def get_aircraft_speed(aircraft_type):
    if aircraft_type in aircraft_specs:
        nominal_speed = aircraft_specs[aircraft_type]['speed']
        return nominal_speed * random.uniform(0.8, 1.0)  # Variance in speed
    return 850 * random.uniform(0.8, 1.0)

def generate_unique_flight_id():
    existing_ids = {flight['id'] for flight in flights}
    while True:
        flight_id = f"EA{random.randint(1,9999):04d}"
        if flight_id not in existing_ids:
            return flight_id
# Haversine distance calculation
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# Calculate bearing between two points
def calculate_bearing(lat1, lon1, lat2, lon2):
    dlon = math.radians(lon2 - lon1)
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    x = math.sin(dlon) * math.cos(lat2_rad)
    y = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon)
    bearing = math.atan2(x, y)
    bearing = math.degrees(bearing)
    return (bearing + 360) % 360

# Select geographically closer waypoints
def select_closer_waypoints(origin, destination, num=3):
    if origin not in airport_coords or destination not in airport_coords:
        return random.sample([wp for wp in waypoints if wp != origin and wp != destination], min(num, len(waypoints) - 2))

    origin_lat, origin_lon = airport_coords[origin]
    dest_lat, dest_lon = airport_coords[destination]
    straight_dist = haversine(origin_lat, origin_lon, dest_lat, dest_lon)
    bearing = calculate_bearing(origin_lat, origin_lon, dest_lat, dest_lon)

    candidates = []
    for wp in waypoints:
        if wp in airport_coords and wp != origin and wp != destination:
            wp_lat, wp_lon = airport_coords[wp]
            dist_from_origin = haversine(origin_lat, origin_lon, wp_lat, wp_lon)
            dist_to_dest = haversine(wp_lat, wp_lon, dest_lat, dest_lon)
            wp_bearing = calculate_bearing(origin_lat, origin_lon, wp_lat, wp_lon)
            bearing_diff = min(abs(wp_bearing - bearing), 360 - abs(wp_bearing - bearing))
            # Stricter criteria: bearing diff < 30, not too close, not too far, and closer to dest than to origin
            if bearing_diff < 30 and 100 < dist_from_origin < straight_dist * 0.8 and dist_to_dest < dist_from_origin:
                candidates.append((wp, dist_from_origin, bearing_diff))

    # Sort by bearing difference, then distance
    candidates.sort(key=lambda x: (x[2], x[1]))
    selected = [wp for wp, _, _ in candidates[:num]]
    # If not enough, add random others with looser criteria
    if len(selected) < num:
        remaining = [wp for wp in waypoints if wp not in selected and wp != origin and wp != destination and wp in airport_coords]
        for wp in remaining:
            wp_lat, wp_lon = airport_coords[wp]
            dist_from_origin = haversine(origin_lat, origin_lon, wp_lat, wp_lon)
            if 200 < dist_from_origin < straight_dist * 0.9:
                selected.append(wp)
                if len(selected) >= num:
                    break
    return selected[:num]

# Load data from files
def load_data():
    global flights, flight_plans
    if os.path.exists(FLIGHTS_FILE):
        with open(FLIGHTS_FILE, 'r') as f:
            flights = json.load(f)
        # Fix any location that is list instead of dict
        for flight in flights:
            if isinstance(flight.get('location'), list) and len(flight['location']) == 2:
                flight['location'] = {"lat": flight['location'][0], "lon": flight['location'][1]}
    else:
        # Generate 15 random flights
        airports = list(airport_coords.keys())
        flights = []
        for i in range(15):
            origin = random.choice(airports)
            destination = random.choice([a for a in airports if a != origin])
            status = random.choice(["Scheduled", "En Route"])
            aircraft_type = random.choice(aircraft_types)
            if origin in airport_coords:
                lat, lon = airport_coords[origin]
                location = {"lat": lat, "lon": lon}
            else:
                location = {"lat": round(random.uniform(-90,90), 4), "lon": round(random.uniform(-180,180), 4)}
            if status == "En Route":
                if destination in airport_coords:
                    lat1, lon1 = airport_coords[origin]
                    lat2, lon2 = airport_coords[destination]
                    frac = random.uniform(0.1, 0.9)
                    lat = lat1 + frac * (lat2 - lat1)
                    lon = lon1 + frac * (lon2 - lon1)
                    location = {"lat": round(lat, 4), "lon": round(lon, 4)}
            fuel_percent = random.randint(50, 100)
            # Estimate fuel_required roughly
            if origin in airport_coords and destination in airport_coords:
                dist_km = haversine(airport_coords[origin][0], airport_coords[origin][1], airport_coords[destination][0], airport_coords[destination][1])
                fuel_kg = dist_km / 10 * 5  # rough estimate
                fuel_required = f"{round(fuel_kg, 2)} kg"
            else:
                fuel_required = f"{random.randint(5000, 20000)} kg"
            flight = {
                "id": f"EA{random.randint(100,999)}",
                "origin": origin,
                "destination": destination,
                "status": status,
                "location": location,
                "fuel": f"{fuel_percent}%",
                "weather": random.choice(["Clear", "Cloudy", "Rainy"]),
                "aircraft_type": aircraft_type,
                "fuel_required": fuel_required
            }
            flights.append(flight)
        save_flights()

    if os.path.exists(FLIGHT_PLANS_FILE):
        with open(FLIGHT_PLANS_FILE, 'r') as f:
            flight_plans = json.load(f)
    else:
        flight_plans = []
        save_flight_plans()

    # Update locations for en route flights
    for flight in flights:
        if flight.get('status') == 'En Route':
            origin = flight.get('origin')
            dest = flight.get('destination')
            if origin in airport_coords and dest in airport_coords:
                lat1, lon1 = airport_coords[origin]
                lat2, lon2 = airport_coords[dest]
                frac = random.uniform(0.1, 0.9)
                lat = lat1 + frac * (lat2 - lat1)
                lon = lon1 + frac * (lon2 - lon1)
                flight['location'] = {"lat": round(lat, 4), "lon": round(lon, 4)}
                # Set fuel to lower for en route
                flight['fuel'] = f"{random.randint(10,84)}%"

# Save data to files
def save_flights():
    with open(FLIGHTS_FILE, 'w') as f:
        json.dump(flights, f, indent=4)

def save_flight_plans():
    with open(FLIGHT_PLANS_FILE, 'w') as f:
        json.dump(flight_plans, f, indent=4)

# Initialize data
flights = []
flight_plans = []
load_data()

# Route: Serve front-end
@app.route('/')
def index():
    return render_template('index.html')

# Route: Monitor real-time flight progress
@app.route('/flights', methods=['GET'])
def get_flights():
    return jsonify(flights)

def generate_unique_flight_id():
    existing_ids = {f['id'] for f in flights}
    while True:
        num = random.randint(1, 9999)
        flight_id = f"EA{num:04d}"
        if flight_id not in existing_ids:
            return flight_id

# Route: Get flight details
@app.route('/flight/<flight_id>', methods=['GET'])
def get_flight(flight_id):
    flight = next((f for f in flights if f["id"] == flight_id), None)
    if flight:
        # Add speed and time remaining if en route
        if flight.get('status') == 'En Route' and flight.get('aircraft_type') in aircraft_specs:
            speed_kmh = get_aircraft_speed(flight['aircraft_type'])
            speed_knots = speed_kmh * 0.539957
            dest_lat, dest_lon = airport_coords.get(flight['destination'], (0, 0))
            current_lat = flight['location']['lat']
            current_lon = flight['location']['lon']
            dist_to_dest_km = haversine(current_lat, current_lon, dest_lat, dest_lon)
            dist_to_dest_nm = dist_to_dest_km * 0.539957
            time_remaining_hours = dist_to_dest_nm / speed_knots if speed_knots > 0 else 0
            flight['speed_knots'] = round(speed_knots, 1)
            flight['time_remaining_hours'] = round(time_remaining_hours, 1)
        
        # Find associated plan
        plan = None
        if 'plan_id' in flight:
            plan_id = flight['plan_id']
            if 0 <= plan_id < len(flight_plans):
                plan = flight_plans[plan_id]
        
        return jsonify({"flight": flight, "plan": plan})
    return jsonify({"error": "Flight not found"}), 404

# Helper: Get random airports
def get_random_airports():
    with open("iata_airport_codes.txt", 'r') as f:
        codes = [line.strip() for line in f.readlines()]
    a1 = random.choice(codes)
    a2 = random.choice(codes)
    while a1 == a2:
        a2 = random.choice(codes)
    return a1, a2

# Route: Generate flight plan locally (made-up data)
@app.route('/generate_plan', methods=['POST'])
def generate_plan_route():
    data = request.json
    origin = data.get('origin')
    destination = data.get('destination')
    aircraft_type = data.get('aircraft_type')
    if not origin or not destination:
        origin, destination = get_random_airports()

    plan = generate_plan(origin, destination, aircraft_type)
    return jsonify(plan)

def generate_plan(origin, destination, aircraft_type=None):
    # Calculate straight distance in nautical miles
    straight_distance_nm = 0
    if origin in airport_coords and destination in airport_coords:
        straight_distance_km = haversine(airport_coords[origin][0], airport_coords[origin][1], airport_coords[destination][0], airport_coords[destination][1])
        straight_distance_nm = straight_distance_km * 0.539957  # km to nm

    # Generate route
    if straight_distance_nm < 100:
        route = [origin, destination]
        total_distance_km = straight_distance_km
    else:
        max_attempts = 3
        for attempt in range(max_attempts):
            num_waypoints = max(1, random.randint(1, 3) - attempt)  # Reduce waypoints on retries
            route_waypoints = select_closer_waypoints(origin, destination, num_waypoints)
            route = [origin] + route_waypoints + [destination]
            # Calculate total distance
            total_distance_km = 0
            prev = origin
            for point in route[1:]:
                if point in airport_coords:
                    total_distance_km += haversine(airport_coords[prev][0], airport_coords[prev][1], airport_coords[point][0], airport_coords[point][1])
                prev = point
            if total_distance_km <= straight_distance_km * 1.5:
                break
        # If still bad, use direct
        if total_distance_km > straight_distance_km * 1.5:
            route = [origin, destination]
            total_distance_km = straight_distance_km

    weather = random.choice(["Clear", "Cloudy", "Rainy", "Stormy"])

    # Fuel estimation
    fuel_required_kg = 0
    speed_kmh = get_aircraft_speed(aircraft_type)
    if aircraft_type and aircraft_type in aircraft_specs and total_distance_km > 0:
        burn_kgh = aircraft_specs[aircraft_type]["burn"]
        time_hours = total_distance_km / speed_kmh
        fuel_required_kg = time_hours * burn_kgh + 0.75 * burn_kgh  # reserve
    fuel_required = f"{round(fuel_required_kg, 2)} kg" if fuel_required_kg > 0 else f"{random.randint(5000, 20000)} lbs"

    plan = {
        "origin": origin,
        "destination": destination,
        "route": route,
        "fuel_required": fuel_required,
        "weather": weather,
        "total_distance": round(total_distance_km * 0.539957, 2),  # nm
        "straight_distance": round(straight_distance_nm, 2),  # nm
        "aircraft_type": aircraft_type
    }
    flight_plans.append(plan)
    save_flight_plans()
    return plan

# Route: Get all generated flight plans
@app.route('/flightplans', methods=['GET'])
def get_flight_plans():
    return jsonify(flight_plans)

# Route: Add a new flight (for persistence demo)
@app.route('/add_flight', methods=['POST'])
def add_flight():
    try:
        data = request.json
        aircraft_type = data.get('aircraft_type', random.choice(aircraft_types))
        origin = data.get('origin', 'JFK')
        flight_id = generate_unique_flight_id()
        new_flight = {
            "id": flight_id,
            "origin": origin,
            "destination": data.get('destination', 'LAX'),
            "status": "Scheduled",
            "fuel": f"{random.randint(50,100)}%",
            "weather": random.choice(["Clear", "Cloudy", "Rainy"]),
            "aircraft_type": aircraft_type
        }
        if origin in airport_coords:
            lat, lon = airport_coords[origin]
            new_flight["location"] = {"lat": lat, "lon": lon}
        else:
            new_flight["location"] = {"lat": round(random.uniform(-90,90), 4), "lon": round(random.uniform(-180,180), 4)}
        flights.append(new_flight)
        save_flights()
        # Generate plan
        plan = generate_plan(new_flight['origin'], new_flight['destination'], aircraft_type)
        new_flight["fuel_required"] = plan["fuel_required"]
        new_flight["plan_id"] = len(flight_plans) - 1  # Index of the plan
        return jsonify({"flight": new_flight, "plan": plan})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)