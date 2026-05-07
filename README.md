# NeXGen Flight Dispatch System

A locally hosted flight dispatch and management system for Efficient Airways. This release contains the current stable implementation with realistic flight behavior, local data persistence, and a modern web interface.

## Overview

The NeXGen Flight Dispatch System is a web application that lets users:
- View and monitor active flights in real-time
- Generate and review flight plans
- Add new flights to the system
- Track aircraft with lat/long coordinates and Google Maps integration
- View realistic fuel data and nearest-airport information for en-route aircraft

All flight data is stored locally in JSON files so the application can run without external APIs.

## New Project Enhancements

This release includes the following key changes:
- **Google Maps support** for quick lat/long preview
- **Nearest airport detection** for en-route flights
- **Origin/destination city mapping** for IATA codes
- **Realistic fuel modeling** with aircraft-specific tank capacities
- **Fuel safety minimum** enforced at 20%
- **Input validation** for airport codes
- **Improved error handling** for JSON loading and runtime faults
- **Automated unit tests** included in `src/test_main.py`

## Project Structure

```
release/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── data_model.md                # Data structure documentation
├── flights.json                 # Stored flight data
├── flight_plans.json            # Stored flight plan data
└── src/
    ├── main.py                  # Flask backend application
    ├── test_main.py             # Unit tests for backend routes and utilities
    ├── iata-airport-codes.txt   # U.S. airport code list for random generation
    ├── static/
    │   ├── app.js               # Front-end JavaScript logic
    │   └── style.css            # Application styling
    └── templates/
        └── index.html           # HTML template
```

## System Requirements

- **Python**: 3.7 or higher
- **Operating System**: Windows, macOS, or Linux
- **Browser**: Any modern web browser (Chrome, Firefox, Safari, Edge)
- **RAM**: 256MB minimum (512MB recommended)
- **Disk Space**: 50MB for application and data

## Installation & Setup

### Step 1: Check Python
Confirm Python is installed:
```bash
python --version
# or
python3 --version
```

### Step 2: Install Dependencies
From the `release` folder:
```bash
cd release
pip install -r requirements.txt
```

If your system uses `pip3`, run:
```bash
pip3 install -r requirements.txt
```

### Step 3: Verify Flask
```bash
python -c "import flask; print(flask.__version__)"
```

## Running the Application

### Basic Startup

1. Navigate to the source directory:
   ```bash
   cd release/src
   ```

2. Start the Flask app:
   ```bash
   python main.py
   ```

3. Open your browser to:
   ```bash
   http://127.0.0.1:5000
   ```

### Running Automated Tests

Run the included backend tests from the source directory:
```bash
cd release/src
python -m unittest test_main.py
```

### Recommended Virtual Environment

```bash
cd release
python -m venv venv

# Activate the environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
cd src
python main.py
```

## Features

### Flight Monitoring
- **Flight table** with ID, origin, destination, status, and aircraft type
- **Flight details** on selection, including route, location, fuel, weather, and aircraft
- **Open in Maps** button next to coordinates
- **Nearest airport shown** only when a flight is en route

### Flight Planning
- **Route generation** with geographically sensible waypoints
- **Fuel estimation** based on aircraft type, distance, and reserve requirements
- **Distance reporting** in nautical miles for total and straight-line legs
- **Weather assignment** for generated flight plans
- **Plan persistence** saved to `flight_plans.json`

### Flight Operations
- **Add flights** with custom origin, destination, and aircraft type
- **Scheduled flights** start at the origin airport
- **Persistent storage** with local JSON files
- **Fuel management** enforces a minimum 20% fill level

## Data Files

### `flights.json`
Stores the active flight records, including:
- flight ID, origin, destination, status
- current location coordinates
- fuel percentage and aircraft type
- weather and associated flight plan ID

### `flight_plans.json`
Stores generated flight plans with:
- route waypoints
- fuel requirement
- total and straight-line distances
- weather conditions

### `iata-airport-codes.txt`
Contains the list of U.S. IATA airport codes used for random flight generation.

## Troubleshooting

### Address Already in Use
If port 5000 is occupied:
```bash
pkill -f "python main.py"
```
or change the port in `main.py`.

### Missing Flask
If Flask is not installed:
```bash
pip install -r requirements.txt
```

### App Access Issues
If the browser cannot connect:
- Confirm the Flask server is running
- Try `http://localhost:5000`
- Verify the firewall is not blocking port 5000

### Data Save Problems
If flight data does not persist:
- Ensure `release/src` is writable
- Delete `flights.json` and `flight_plans.json` to regenerate data

## Usage Guide

### Viewing Flights
1. Open the app in a browser
2. Click any flight row to view details
3. Use the Google Maps button to preview coordinates

### Adding Flights
1. Enter origin and destination airport codes
2. Select an aircraft type
3. Click **Add Flight and Generate Plan**
4. The new flight appears in the table, and the generated plan is displayed

## Technical Notes

### Backend
- Uses Flask for routing and JSON APIs
- Includes route validation and safe JSON loading
- Provides realistic routing and fuel calculations

### Frontend
- JavaScript populates flights and plan tables dynamically
- Displays enriched flight details and Google Maps links

### Testing
- Includes a unit test file: `release/src/test_main.py`
- Covers core utilities, API endpoints, and basic behavior

## Recent Enhancements
- Google Maps integration
- Nearest airport detection in miles
- City mapping for origin/destination codes
- Realistic aircraft fuel capacity calculations
- Minimum 20% fuel enforcement
- Route validation and improved error handling
- README and test instructions for release usage

## Support
For a detailed look at the data format and models, see [data_model.md](data_model.md).

## Version Information

**Application**: NeXGen Flight Dispatch System  
**Version**: v1.0  
**Status**: Release  
**Last Updated**: May 2026  
