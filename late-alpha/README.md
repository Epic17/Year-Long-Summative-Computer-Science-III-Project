# Late Alpha - NeXGen Flight Dispatch

This version removes all external API dependencies and operates entirely locally with made-up flight data.

## Features
- View and manage flights (stored in flights.json)
- Generate flight plans with random data (stored in flight_plans.json)
- Add new flights
- Data persistence using JSON files

## Data Model
See data_model.txt for details on data structures.

## Running
1. Install dependencies: `pip install -r requirements.txt`
2. Run: `cd src && python main.py`
3. Open http://127.0.0.1:5000 in browser

## Changes from Previous Versions
- Removed API calls to external flight plan databases
- All data is generated locally
- Added data persistence to JSON files
- Updated data model documentation