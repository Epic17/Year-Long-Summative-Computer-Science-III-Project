// Fetch and display flights
function loadFlights() {
    fetch('/flights')
        .then(res => res.json())
        .then(flights => {
            const list = document.getElementById('flight-list');
            list.innerHTML = '';
            flights.forEach(flight => {
                const li = document.createElement('li');
                li.textContent = `${flight.id}: ${flight.origin} → ${flight.destination} (${flight.status})`;
                li.onclick = () => showFlightDetails(flight.id);
                list.appendChild(li);
            });
        });
}

function showFlightDetails(flightId) {
    fetch(`/flight/${flightId}`)
        .then(res => res.json())
        .then(flight => {
            if (flight.error) {
                document.getElementById('flight-details').textContent = flight.error;
            } else {
                document.getElementById('flight-details').innerHTML = `
                    <strong>ID:</strong> ${flight.id}<br>
                    <strong>Origin:</strong> ${flight.origin}<br>
                    <strong>Destination:</strong> ${flight.destination}<br>
                    <strong>Status:</strong> ${flight.status}<br>
                    <strong>Location:</strong> Lat ${flight.location.lat}, Lon ${flight.location.lon}<br>
                    <strong>Fuel:</strong> ${flight.fuel}<br>
                    <strong>Weather:</strong> ${flight.weather}
                `;
            }
        });
}

// Handle flight plan generation
const planForm = document.getElementById('plan-form');
planForm.onsubmit = function(e) {
    e.preventDefault();
    const origin = planForm.origin.value;
    const destination = planForm.destination.value;
    fetch('/generate_plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ origin, destination })
    })
    .then(res => res.json())
    .then(plan => {
        document.getElementById('plan-result').innerHTML = `
            <strong>Route:</strong> ${Array.isArray(plan.route) ? plan.route.join(' → ') : plan.route}<br>
            <strong>Fuel Required:</strong> ${plan.fuel_required}<br>
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
            const list = document.getElementById('flight-plan-list');
            list.innerHTML = '';
            plans.forEach(plan => {
                const li = document.createElement('li');
                li.innerHTML = `<strong>${plan.origin} → ${plan.destination}</strong>: ${Array.isArray(plan.route) ? plan.route.join(' → ') : plan.route}`;
                list.appendChild(li);
            });
        });
}

// Initial load
loadFlights();
loadFlightPlans();
