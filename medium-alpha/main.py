import requests

url = "https://aerodatabox.p.rapidapi.com/flights/airports/iata/YYZ"

querystring = {"offsetMinutes":"-120","durationMinutes":"720","withLeg":"true","direction":"Both","withCancelled":"true","withCodeshared":"true","withCargo":"true","withPrivate":"true","withLocation":"false"}

headers = {
	"x-rapidapi-key": "d045d3f5e5msh0066a68d332bb9ap120efcjsn3ed3a7bb22f1",
	"x-rapidapi-host": "aerodatabox.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

print(response.json())