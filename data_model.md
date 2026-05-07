# Data Model for Late Alpha

## Flights
Stored in flights.json as a list of dictionaries.
Each flight has:
- id: string (flight identifier)
- origin: string (IATA code)
- destination: string (IATA code)
- status: string (e.g., "En Route", "Scheduled")
- location: dict with lat and lon (floats)
- fuel: string (percentage)
- weather: string (e.g., "Clear", "Cloudy")

## Flight Plans
Stored in flight_plans.json as a list of dictionaries.
Each plan has:
- origin: string (IATA code)
- destination: string (IATA code)
- route: list of strings (waypoints)
- fuel_required: string (e.g., "15000 lbs")
- weather: string (made-up weather condition)

Data is persisted to JSON files for simplicity. No database used.