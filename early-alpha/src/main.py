from flask import Flask, jsonify, request, render_template
import random
import requests

app = Flask(__name__, static_folder='static', template_folder='templates')
# Route: Serve front-end
@app.route('/')
def index():
	return render_template('index.html')

# Sample data structure for flights
flights = [
	{
		"id": "AA123",
		"origin": "JFK",
		"destination": "LAX",
		"status": "En Route",
		"location": {"lat": 40.6413, "lon": -73.7781},
		"fuel": "75%",
		"weather": "Clear"
	},
	{
		"id": "DL456",
		"origin": "ATL",
		"destination": "ORD",
		"status": "Scheduled",
		"location": {"lat": 33.6407, "lon": -84.4277},
		"fuel": "100%",
		"weather": "Cloudy"
	}
]

# Route: Monitor real-time flight progress
@app.route('/flights', methods=['GET'])
def get_flights():
	return jsonify(flights)

# Route: View current and past flight plans
@app.route('/flight/<flight_id>', methods=['GET'])
def get_flight_plan(flight_id):
	flight = next((f for f in flights if f["id"] == flight_id), None)
	if flight:
		return jsonify(flight)
	return jsonify({"error": "Flight not found"}), 404


# Store generated flight plans
flight_plans = []

# Helper: Get random airports
def get_random_airports():
	a1 = random.choice(open("iata_airport_codes.txt").readlines()).strip()
	a2 = random.choice(open("iata_airport_codes.txt").readlines()).strip()
	return a1, a2

# Route: Generate flight plan using Flight Plan Database API
@app.route('/generate_plan', methods=['POST'])
def generate_plan():
	data = request.json
	origin = data.get('origin')
	destination = data.get('destination')
	if not origin or not destination:
		origin, destination = get_random_airports()

	# Call Flight Plan Database API with HTTP Basic Auth
	api_url = "https://flightplandatabase.com/api/flightplan"
	with open("api_key.txt") as f:
		api_key = f.read().strip()
	payload = {"fromICAO": origin, "toICAO": destination}
	resp = requests.post(api_url, json=payload, auth=(api_key, ""))
	if resp.status_code == 200:
		fp = resp.json()
		plan = {
			"origin": origin,
			"destination": destination,
			"route": fp.get("route", []),
			"fuel_required": fp.get("fuel", "N/A"),
			"weather": "To be fetched from API"
		}
		flight_plans.append(plan)
		return jsonify(plan)
	else:
		return jsonify({"error": "Failed to generate flight plan."}), 500

# Route: Get all generated flight plans
@app.route('/flightplans', methods=['GET'])
def get_flight_plans():
	return jsonify(flight_plans)

if __name__ == '__main__':
	app.run(debug=True)
