import flask
import random
import json
import os
import math

app = flask.Flask(__name__, static_folder='static', template_folder='templates')

# Data persistence files
RELEASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
FLIGHTS_FILE = os.path.join(RELEASE_DIR, "flights.json")
FLIGHT_PLANS_FILE = os.path.join(RELEASE_DIR, "flight_plans.json")
AIRPORT_COORDS_FILE = os.path.join(RELEASE_DIR, "airport_coords.json")

# Aircraft types
aircraft_types = [
    "Boeing 737-800", "Boeing 737 MAX-8", "Boeing 737 MAX-9",
    "Airbus A319", "Airbus A319neo", "Airbus A320", "Airbus A320neo",
    "Airbus A321", "Airbus A321neo", "Airbus A321XLR", "Airbus A330",
    "Boeing 757", "Boeing 767", "Boeing 777", "Boeing 787", "Airbus A350"
]

# U.S. waypoints/VORs
waypoints = [
    "ATL", "BOS", "ORD", "DFW", "DEN", "SEA", "SFO", "LAX", "PHX", "LAS",
    "MSP", "DTW", "CLE", "PIT", "BWI", "IAD", "CLT", "RDU", "BNA", "MEM",
    "STL", "CVG", "IND", "CMH", "SDF", "MSY", "HOU", "SAT", "AUS", "ELP",
    "ABQ", "OKC", "TUL", "DSM", "OMA", "ICT", "MCI", "SLC", "BOI", "GEG", "PDX"
]

# Airport coordinates are loaded from a separate JSON file to make the data easier to maintain.
airport_coords = {}

vor_coords = airport_coords  # Approximate VOR coords to airport coords

# IATA code to city mapping
airport_cities = {
    "JFK": "New York, NY",
    "LAX": "Los Angeles, CA",
    "ATL": "Atlanta, GA",
    "ORD": "Chicago, IL",
    "DFW": "Dallas/Fort Worth, TX",
    "DEN": "Denver, CO",
    "SEA": "Seattle, WA",
    "SFO": "San Francisco, CA",
    "PHX": "Phoenix, AZ",
    "LAS": "Las Vegas, NV",
    "MSP": "Minneapolis, MN",
    "DTW": "Detroit, MI",
    "CLE": "Cleveland, OH",
    "PIT": "Pittsburgh, PA",
    "BWI": "Baltimore, MD",
    "IAD": "Washington, DC",
    "CLT": "Charlotte, NC",
    "RDU": "Raleigh, NC",
    "BNA": "Nashville, TN",
    "MEM": "Memphis, TN",
    "STL": "St. Louis, MO",
    "CVG": "Cincinnati, OH",
    "IND": "Indianapolis, IN",
    "CMH": "Columbus, OH",
    "SDF": "Louisville, KY",
    "MSY": "New Orleans, LA",
    "HOU": "Houston, TX",
    "SAT": "San Antonio, TX",
    "AUS": "Austin, TX",
    "ELP": "El Paso, TX",
    "ABQ": "Albuquerque, NM",
    "OKC": "Oklahoma City, OK",
    "TUL": "Tulsa, OK",
    "DSM": "Des Moines, IA",
    "OMA": "Omaha, NE",
    "ICT": "Wichita, KS",
    "MCI": "Kansas City, MO",
    "SLC": "Salt Lake City, UT",
    "BOI": "Boise, ID",
    "GEG": "Spokane, WA",
    "PDX": "Portland, OR",
}

# Aircraft specs: speed (km/h), burn (kg/h), fuel_capacity_kg
aircraft_specs = {
    "Boeing 737-800": {"speed": 850, "burn": 2500, "fuel_capacity_kg": 11887},
    "Boeing 737 MAX-8": {"speed": 850, "burn": 2500, "fuel_capacity_kg": 11887},
    "Boeing 737 MAX-9": {"speed": 850, "burn": 2600, "fuel_capacity_kg": 12972},
    "Airbus A319": {"speed": 830, "burn": 2200, "fuel_capacity_kg": 12329},
    "Airbus A319neo": {"speed": 830, "burn": 2100, "fuel_capacity_kg": 12329},
    "Airbus A320": {"speed": 830, "burn": 2400, "fuel_capacity_kg": 12329},
    "Airbus A320neo": {"speed": 830, "burn": 2300, "fuel_capacity_kg": 12329},
    "Airbus A321": {"speed": 830, "burn": 2600, "fuel_capacity_kg": 14900},
    "Airbus A321neo": {"speed": 830, "burn": 2500, "fuel_capacity_kg": 14900},
    "Airbus A321XLR": {"speed": 830, "burn": 2500, "fuel_capacity_kg": 20232},
    "Airbus A330": {"speed": 870, "burn": 6500, "fuel_capacity_kg": 63000},
    "Boeing 757": {"speed": 850, "burn": 3500, "fuel_capacity_kg": 19730},
    "Boeing 767": {"speed": 850, "burn": 5200, "fuel_capacity_kg": 34799},
    "Boeing 777": {"speed": 890, "burn": 7000, "fuel_capacity_kg": 23231},
    "Boeing 787": {"speed": 900, "burn": 5400, "fuel_capacity_kg": 90718},
    "Airbus A350": {"speed": 900, "burn": 6800, "fuel_capacity_kg": 63034},
}

def get_aircraft_speed(aircraft_type):
    """Return realistic cruise speed for an aircraft type with some variance."""
    if aircraft_type in aircraft_specs:
        nominal_speed = aircraft_specs[aircraft_type]['speed']
        return nominal_speed * random.uniform(0.8, 1.0)  # Variance in speed
    return 850 * random.uniform(0.8, 1.0)

# Find the nearest airport to a given location
def find_nearest_airport(lat, lon):
    nearest_airport = None
    min_distance = float('inf')
    
    for airport_code, (airport_lat, airport_lon) in airport_coords.items():
        distance = haversine(lat, lon, airport_lat, airport_lon)
        if distance < min_distance:
            min_distance = distance
            nearest_airport = airport_code
    
    return nearest_airport, min_distance

# Ensure fuel doesn't go below 20%
def ensure_minimum_fuel(fuel_percent_str):
    """Clamp a fuel percentage string to at least 30%."""
    try:
        fuel_percent = int(fuel_percent_str.replace('%', '').strip())
        if fuel_percent < 30:
            fuel_percent = 30
        return f"{fuel_percent}%"
    except ValueError:
        return fuel_percent_str

# Normalize an IATA airport code string
def normalize_airport_code(code):
    """Return a normalized IATA code if it looks valid, otherwise None."""
    if not isinstance(code, str):
        return None
    code = code.strip().upper()
    return code if len(code) == 3 and code.isalpha() else None

# Validate an IATA airport code against the known airport list
def validate_airport_code(code):
    """Return a normalized airport code if it is known, otherwise None."""
    code = normalize_airport_code(code)
    return code if code in airport_coords else None

# Safely load JSON data from a file
def safe_load_json(path, default):
    """Load JSON from path, returning default if the file is missing or malformed."""
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return default

# Load the airport coordinate mapping from a separate file
def load_airport_coords():
    global airport_coords, vor_coords
    coords = safe_load_json(AIRPORT_COORDS_FILE, {})
    airport_coords = {
        code: tuple(coords[code])
        for code in coords
        if isinstance(coords[code], (list, tuple)) and len(coords[code]) == 2
    }
    vor_coords = airport_coords

# Generates a unique flight ID
def generate_unique_flight_id():
    """Return a new flight ID that does not collide with existing flights."""
    existing_ids = {flight['id'] for flight in flights}
    while True:
        flight_id = f"EA{random.randint(1,9999):04d}"
        if flight_id not in existing_ids:
            return flight_id

# Haversine distance calculation
def haversine(lat1, lon1, lat2, lon2):
    """Calculate the great-circle distance between two latitude/longitude points in kilometers."""
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# Calculate bearing between two points
def calculate_bearing(lat1, lon1, lat2, lon2):
    """Calculate the bearing from point A to point B in degrees."""
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
    """Return waypoints that generally lie between the origin and destination.

    This helps create a more natural route for mid-range flights.
    """
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


def route_progresses_toward_destination(route, destination, max_increase_km=50):
    """Return True when the route generally moves closer to the destination at each step."""
    if destination not in airport_coords:
        return False

    prev_distance = None
    dest_lat, dest_lon = airport_coords[destination]
    for waypoint in route:
        if waypoint not in airport_coords:
            return False
        waypoint_lat, waypoint_lon = airport_coords[waypoint]
        current_distance = haversine(waypoint_lat, waypoint_lon, dest_lat, dest_lon)
        if prev_distance is not None and current_distance > prev_distance + max_increase_km:
            return False
        prev_distance = current_distance
    return True

# Load data from files
def load_data():
    """Load flights and flight plans from the local JSON persistence files."""
    global flights, flight_plans
    flights = safe_load_json(FLIGHTS_FILE, [])
    if flights:
        # Fix any location that is list instead of dict
        for flight in flights:
            if isinstance(flight.get('location'), list) and len(flight['location']) == 2:
                flight['location'] = {"lat": flight['location'][0], "lon": flight['location'][1]}
    else:

        # Generate 15 random flights and produce associated flight plans
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
            fuel_percent = max(30, random.randint(50, 100))  # Ensure minimum 30%
            # Estimate fuel_required roughly
            if origin in airport_coords and destination in airport_coords:
                dist_km = haversine(airport_coords[origin][0], airport_coords[origin][1], airport_coords[destination][0], airport_coords[destination][1])
                fuel_kg = dist_km / 10 * 5  # rough estimate
                fuel_required = f"{round(fuel_kg, 2)} kg"
            else:
                fuel_required = f"{random.randint(5000, 20000)} kg"
            flight = {
                "id": f"EA{random.randint(1, 999)}",
                "origin": origin,
                "destination": destination,
                "status": status,
                "location": location,
                "fuel": f"{fuel_percent}%",
                "weather": random.choice(["Clear", "Cloudy", "Rainy"]),
                "aircraft_type": aircraft_type,
                "fuel_required": fuel_required
            }
            plan = generate_plan(origin, destination, aircraft_type)
            flight["fuel_required"] = plan["fuel_required"]
            flight["plan_id"] = len(flight_plans) - 1
            flights.append(flight)
        save_flights()

    flight_plans = safe_load_json(FLIGHT_PLANS_FILE, [])
    if not flight_plans:
        flight_plans = []
        if flights:
            for flight in flights:
                origin = flight.get('origin')
                destination = flight.get('destination')
                if origin and destination:
                    plan = generate_plan(origin, destination, flight.get('aircraft_type'))
                    flight['plan_id'] = len(flight_plans) - 1
            save_flight_plans()
            save_flights()
        else:
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
                # Set fuel to lower for en route, but minimum 30%
                flight['fuel'] = f"{max(30, random.randint(10,84))}%"

# Save data to files
def save_flights():
    with open(FLIGHTS_FILE, 'w') as f:
        json.dump(flights, f, indent=4)

def save_flight_plans():
    with open(FLIGHT_PLANS_FILE, 'w') as f:
        json.dump(flight_plans, f, indent=4)

# Route: Serve front-end
@app.route('/')
def index():
    return flask.render_template('index.html')

# Route: Monitor real-time flight progress
@app.route('/flights', methods=['GET'])
def get_flights():
    """API endpoint to return the current list of stored flights."""
    return flask.jsonify(flights)

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
            raw_time_hours = dist_to_dest_nm / speed_knots if speed_knots > 0 else 0
            time_remaining_hours = raw_time_hours * 1.15  # Add 15% for descent, approach, landing
            total_minutes = round(time_remaining_hours * 60)
            hours = total_minutes // 60
            minutes = total_minutes % 60
            if hours > 0 and minutes > 0:
                time_remaining_display = f"{hours}h {minutes}m"
            elif hours > 0:
                time_remaining_display = f"{hours}h"
            else:
                time_remaining_display = f"{minutes} minutes"

            flight['speed_knots'] = round(speed_knots, 1)
            flight['distance_remaining_nm'] = round(dist_to_dest_nm, 1)
            flight['distance_remaining_km'] = round(dist_to_dest_km, 1)
            flight['time_remaining_hours'] = round(time_remaining_hours, 2)
            flight['time_remaining_display'] = time_remaining_display

            # Find nearest airport to current location (only for en-route flights)
            if 'location' in flight:
                nearest_airport, distance_km = find_nearest_airport(flight['location']['lat'], flight['location']['lon'])
                flight['nearest_airport'] = nearest_airport
                flight['nearest_airport_distance'] = round(distance_km * 0.539957, 1)  # convert km to nautical miles
        
        # Add city names for origin and destination
        flight['origin_city'] = airport_cities.get(flight.get('origin'), 'Unknown')
        flight['destination_city'] = airport_cities.get(flight.get('destination'), 'Unknown')
        
        # Add fuel capacity if aircraft type is known
        if flight.get('aircraft_type') in aircraft_specs:
            flight['fuel_capacity_kg'] = aircraft_specs[flight['aircraft_type']]['fuel_capacity_kg']
        
        # Find associated plan
        plan = None
        if 'plan_id' in flight:
            plan_id = flight['plan_id']
            if 0 <= plan_id < len(flight_plans):
                plan = flight_plans[plan_id]
        
        return flask.jsonify({"flight": flight, "plan": plan})
    return flask.jsonify({"error": "Flight not found"}), 404

# Helper: Get random airports
def get_random_airports():
    """Return two distinct random airport codes from the local IATA airport list."""
    with open("iata_airport_codes.txt", 'r') as f:
        codes = [line.strip() for line in f.readlines() if line.strip()]
    a1 = random.choice(codes)
    a2 = random.choice(codes)
    while a1 == a2:
        a2 = random.choice(codes)
    return a1, a2

# Route: Generate flight plan locally (made-up data)
@app.route('/generate_plan', methods=['POST'])
def generate_plan_route():
    """API endpoint to generate a flight plan for a requested origin and destination."""
    data = flask.request.json or {}
    origin = normalize_airport_code(data.get('origin'))
    destination = normalize_airport_code(data.get('destination'))
    aircraft_type = data.get('aircraft_type')

    if not origin or not destination:
        origin, destination = get_random_airports()

    plan = generate_plan(origin, destination, aircraft_type)
    return flask.jsonify(plan)

# Generate a flight plan with more realistic routing and fuel estimation
def generate_plan(origin, destination, aircraft_type=None):
    """Build a flight plan including route, fuel requirements, weather, and distances."""

    # Calculate straight distance in nautical miles
    straight_distance_nm = 0
    if origin in airport_coords and destination in airport_coords:
        straight_distance_km = haversine(airport_coords[origin][0], airport_coords[origin][1], airport_coords[destination][0], airport_coords[destination][1])
        straight_distance_nm = straight_distance_km * 0.539957  # km to nm

    # Generate route
    if straight_distance_nm < 100:
        route = [origin, destination]
        total_distance_km = straight_distance_km if 'straight_distance_km' in locals() else 0
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
            if total_distance_km <= straight_distance_km * 1.5 and route_progresses_toward_destination(route, destination):
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

# Initialize data
flights = []
flight_plans = []
load_airport_coords()
load_data()

# Route: Get all generated flight plans
@app.route('/flightplans', methods=['GET'])
def get_flight_plans():
    return flask.jsonify(flight_plans)

# Route: Add a new flight (for persistence demo)
@app.route('/add_flight', methods=['POST'])
def add_flight():
    """API endpoint to create a new flight and generate an associated flight plan."""
    try:
        data = flask.request.json or {}
        aircraft_type = data.get('aircraft_type', random.choice(aircraft_types))
        origin = normalize_airport_code(data.get('origin')) or 'JFK'
        destination = normalize_airport_code(data.get('destination')) or 'LAX'
        flight_id = generate_unique_flight_id()
        new_flight = {
            "id": flight_id,
            "origin": origin,
            "destination": destination,
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
        
        # Add city names and fuel capacity
        new_flight['origin_city'] = airport_cities.get(new_flight['origin'], 'Unknown')
        new_flight['destination_city'] = airport_cities.get(new_flight['destination'], 'Unknown')
        if new_flight.get('aircraft_type') in aircraft_specs:
            new_flight['fuel_capacity_kg'] = aircraft_specs[new_flight['aircraft_type']]['fuel_capacity_kg']
        
        return flask.jsonify({"flight": new_flight, "plan": plan})
    except Exception as e:
        return flask.jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)