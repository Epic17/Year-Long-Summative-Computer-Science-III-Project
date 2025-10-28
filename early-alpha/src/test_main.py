# early-alpha/src/test_main.py
import unittest
from unittest.mock import patch, Mock
import io
import builtins

# Absolute import from the src package (namespace package)
from src.main import app

class TestMain(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_get_flights(self):
        res = self.client.get('/flights')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIsInstance(data, list)
        self.assertTrue(any(f.get('id') == 'AA123' for f in data))

    def test_get_flight_plan_found(self):
        res = self.client.get('/flight/AA123')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get('id'), 'AA123')

    def test_get_flight_plan_not_found(self):
        res = self.client.get('/flight/NOPE')
        self.assertEqual(res.status_code, 404)

    def test_generate_plan_success(self):
        # Save real open to delegate for non-mocked files
        real_open = builtins.open

        def fake_open(file, mode='r', *args, **kwargs):
            # Provide fake api key
            if 'api_key.txt' in str(file):
                return io.StringIO('TEST_API_KEY')
            # Provide fake IATA codes if needed
            if 'iata_airport_codes.txt' in str(file):
                return io.StringIO('KJFK\nKLAX\n')
            # Fallback to real open for any other files
            return real_open(file, mode, *args, **kwargs)

        # Create a mock response for requests.post used in generate_plan
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {'route': ['TEST1', 'TEST2'], 'fuel': '5000kg'}

        # Patch the open used in src.main and patch requests.post used in src.main
        with patch('src.main.open', side_effect=fake_open):
            with patch('src.main.requests.post', return_value=mock_resp) as mock_post:
                res = self.client.post('/generate_plan', json={'origin': 'KJFK', 'destination': 'KLAX'})
                self.assertEqual(res.status_code, 200)
                data = res.get_json()
                self.assertEqual(data.get('origin'), 'KJFK')
                self.assertEqual(data.get('destination'), 'KLAX')
                # Ensure route and fuel came from mocked API response
                self.assertEqual(data.get('route'), ['TEST1', 'TEST2'])
                self.assertEqual(data.get('fuel_required'), '5000kg' or data.get('fuel_required') == '5000kg')

        # Verify flight plan was added to /flightplans
        res2 = self.client.get('/flightplans')
        self.assertEqual(res2.status_code, 200)
        plans = res2.get_json()
        self.assertTrue(any(p.get('origin') == 'KJFK' and p.get('destination') == 'KLAX' for p in plans))

if __name__ == '__main__':
    unittest.main()