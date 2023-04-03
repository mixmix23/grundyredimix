import googlemaps
from googlemaps.geometry._types import Point
from googlemaps.geometry import is_point_in_polygon


# Read the API key from api_key.txt
with open('api_key.txt', 'r') as file:
    api_key = file.readline().strip()

# Initialize the Google Maps API client with the API key
gmaps = googlemaps.Client(key=api_key)

# Define the vertices of the polygon
vertices = [
    {'lat': 40.7128, 'lng': -74.0060},  # New York City
    {'lat': 37.7749, 'lng': -122.4194},  # San Francisco
    {'lat': 34.0522, 'lng': -118.2437}  # Los Angeles
]

# Convert the address to a latitude and longitude
geocode_result = gmaps.geocode('1600 Amphitheatre Parkway, Mountain View, CA')
location = geocode_result[0]['geometry']['location']
point = Point(location['lat'], location['lng'])

# Check if the point is inside the polygon
is_inside = is_point_in_polygon(point, vertices)

print(is_inside)  # This should print False