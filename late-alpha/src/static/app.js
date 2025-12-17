// Fetch and display flights
function loadFlights() {
    fetch('/flights')
        .then(res => res.json())
        .then(flights => {
            const tbody = document.getElementById('flights-tbody');
            tbody.innerHTML = '';
            flights.forEach(flight => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${flight.id}</td>
                    <td>${flight.origin}</td>
                    <td>${flight.destination}</td>
                    <td>${flight.status}</td>
                    <td>${flight.aircraft_type}</td>
                `;
                tr.onclick = () => showFlightDetails(flight.id);
                tbody.appendChild(tr);
            });
        });
}

function showFlightDetails(flightId) {
    fetch(`/flight/${flightId}`)
        .then(res => res.json())
        .then(data => {
            const flight = data.flight;
            const plan = data.plan;
            if (flight.error) {
                document.getElementById('flight-details').textContent = flight.error;
            } else {
                let fuel_display = flight.fuel;
                if (flight.fuel_required) {
                    const fuel_percent = parseInt(flight.fuel) / 100;
                    const fuel_required_kg = parseFloat(flight.fuel_required.split(' ')[0]);
                    const fuel_remaining_kg = fuel_percent * fuel_required_kg;
                    const fuel_remaining_lbs = Math.round(fuel_remaining_kg * 2.20462);
                    const fuel_required_lbs = Math.round(fuel_required_kg * 2.20462);
                    fuel_display += ` (${fuel_remaining_lbs}/${fuel_required_lbs} lbs)`;
                }
                let details = `
                    <strong>ID:</strong> ${flight.id}<br>
                    <strong>Origin:</strong> ${flight.origin}<br>
                    <strong>Destination:</strong> ${flight.destination}<br>
                    <strong>Status:</strong> ${flight.status}<br>
                    <strong>Location:</strong> Lat ${flight.location.lat}, Lon ${flight.location.lon}<br>
                    <strong>Fuel:</strong> ${fuel_display}<br>
                    <strong>Weather:</strong> ${flight.weather}<br>
                    <strong>Aircraft Type:</strong> ${flight.aircraft_type}
                `;
                if (plan) {
                    details += `<br><br><strong>Flight Plan:</strong><br>
                    <strong>Route:</strong> ${plan.route.join(' → ')}<br>
                    <strong>Total Distance:</strong> ${plan.total_distance} nm<br>
                    <strong>Straight Distance:</strong> ${plan.straight_distance} nm`;
                }
                if (flight.speed_knots) {
                    details += `<br><strong>Speed:</strong> ${flight.speed_knots} knots<br>
                    <strong>Time Remaining:</strong> ${flight.time_remaining_hours} hours`;
                }
                document.getElementById('flight-details').innerHTML = details;
            }
        });
}

// Handle adding new flight
const addFlightForm = document.getElementById('add-flight-form');
addFlightForm.onsubmit = function(e) {
    e.preventDefault();
    const origin = addFlightForm.origin.value || 'JFK';
    const destination = addFlightForm.destination.value || 'LAX';
    const aircraft_type = addFlightForm.aircraft_type.value;
    fetch('/add_flight', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ origin, destination, aircraft_type })
    })
    .then(res => res.json())
    .then(data => {
        const flight = data.flight;
        const plan = data.plan;
        loadFlights();
        addFlightForm.reset();
        // Display the generated plan
        const fuel_kg = parseFloat(plan.fuel_required.split(' ')[0]);
        const fuel_lbs = Math.round(fuel_kg * 2.20462);
        document.getElementById('plan-result').innerHTML = `
            <strong>Generated Plan:</strong><br>
            <strong>Route:</strong> ${plan.route.join(' → ')}<br>
            <strong>Total Distance:</strong> ${plan.total_distance} nm<br>
            <strong>Straight Distance:</strong> ${plan.straight_distance} nm<br>
            <strong>Fuel Required:</strong> ${fuel_lbs} lbs<br>
            <strong>Weather:</strong> ${plan.weather}
        `;
        loadFlightPlans();
    });
};



// Fetch and display generated flight plans
function loadFlightPlans() {
    fetch('/flightplans')
        .then(res => res.json())
        .then(plans => {
            const tbody = document.getElementById('plans-tbody');
            tbody.innerHTML = '';
            plans.forEach(plan => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${plan.origin}</td>
                    <td>${plan.destination}</td>
                    <td>${Array.isArray(plan.route) ? plan.route.join(' → ') : plan.route}</td>
                    <td>${plan.aircraft_type || ''}</td>
                `;
                tbody.appendChild(tr);
            });
        });
}

// Initial load
loadFlights();
loadFlightPlans();