import unittest
import main

# Note: These tests assume the Flask app is running and accessible at http://localhost:5000
class MainAppTests(unittest.TestCase):
    def setUp(self):
        self.client = main.app.test_client()

    # Test the haversine distance calculation between JFK and LAX
    def test_haversine_distance_between_jfk_and_lax(self):
        distance = main.haversine(40.6413, -73.7781, 33.9425, -118.4081)
        self.assertGreater(distance, 3900)
        self.assertLess(distance, 4100)

    # Test the airport code validation function
    def test_validate_airport_code(self):
        self.assertEqual(main.validate_airport_code('jfk'), 'JFK')
        self.assertIsNone(main.validate_airport_code('XYZ'))
        self.assertIsNone(main.validate_airport_code(None))

    # Test the nearest airport function with coordinates near Denver
    def test_find_nearest_airport(self):
        airport, distance = main.find_nearest_airport(39.8561, -104.6737)
        self.assertEqual(airport, 'DEN')
        self.assertLess(distance, 5)

    # Test the flight plan generation endpoint with valid input
    def test_generate_plan_route_returns_json(self):
        response = self.client.post('/generate_plan', json={'origin': 'JFK', 'destination': 'LAX', 'aircraft_type': 'Boeing 737-800'})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('route', data)
        self.assertIn('fuel_required', data)
        self.assertIn('total_distance', data)

    # Test the flight plan generation endpoint with missing input (should use random airports)
    def test_get_flights_endpoint(self):
        response = self.client.get('/flights')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)

    # Test the flight details endpoint for an existing flight
    def test_get_flight_details_endpoint(self):
        if not main.flights:
            self.skipTest('No flights available for detail lookup')
        flight_id = main.flights[0]['id']
        response = self.client.get(f'/flight/{flight_id}')
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIn('flight', payload)
        self.assertEqual(payload['flight']['id'], flight_id)

if __name__ == '__main__':
    unittest.main()
