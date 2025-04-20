from flask import render_template, request
from flask_app import app
import requests
from geopy.geocoders import GoogleV3
import os

# Retrieve Google Maps API key from environment variables
api_key = os.getenv("GOOGLE_MAPS_API_KEY")##AIzaSyCR3oDGLh4JBoSYOZedCAMQh7VY_63jVMw

# Initialize GoogleV3 geolocator
geolocator = GoogleV3(api_key="AIzaSyCR3oDGLh4JBoSYOZedCAMQh7VY_63jVMw")


STORMGLASS_API_KEY = "5444b2d0-1b36-11f0-bda0-0242ac130003-5444b32a-1b36-11f0-bda0-0242ac130003"
STORMGLASS_URL = "https://api.stormglass.io/v2/weather/point"


@app.route('/')
def index():
    return render_template('index.html')


def classify_wind_direction(wind_direction, coastline_orientation):
    # Calculate difference between wind direction and coastline
    difference = (wind_direction - coastline_orientation) % 360
    if 45 <= difference <= 135:  # Within 45-135° range
        return "Onshore"
    elif 225 <= difference <= 315:  # Within 225-315° range
        return "Offshore"
    else:
        return "Parallel to Shore"


@app.route("/surf_conditions", methods=["POST"])
def surf_conditions():
    # Retrieve user inputs
    location = request.form.get("location")
    country = request.form.get("country")
    province = request.form.get("province")

    if not location:
        return render_template("error.html", message="Please enter a location.")  # Handle empty location input

    # Combine inputs into a full address for geocoding
    full_address = location
    if country:
        full_address += f", {country}"
    if province:  # Add province only if it's provided
        full_address += f", {province}"
    
    print(f"Full address for geocoding: {full_address}")  # Debugging information

    # Step 1: Geocode the location to get latitude and longitude
    try:
        geolocation = geolocator.geocode(full_address)

        if not geolocation:  # Handle invalid or unrecognized locations
            return render_template("error.html", message=f"Could not find '{full_address}'. Try another.")

        # Extract latitude and longitude
        lat, lng = geolocation.latitude, geolocation.longitude
        print(f"Geocoded: lat={lat}, lng={lng}")  # Debugging information
    except Exception as e:
        return render_template("error.html", message=f"Geocoding error: {str(e)}")

    # Step 2: Fetch surf conditions from the Stormglass API
    headers = {"Authorization": STORMGLASS_API_KEY}
    params = {
        "lat": lat,
        "lng": lng,
        "params": "waveHeight,windSpeed,windDirection",
        "source": "sg"  # Primary source
    }

    # Mock Data for Development
    mock_response = {
        'hours': [
            {'waveHeight': {'sg': 0.95}, 'windDirection': {'sg': 240.33}, 'windSpeed': {'sg': 9.06}}
        ]
    }

    try:
        response = requests.get(STORMGLASS_URL, params=params, headers=headers)
        if response.status_code == 200:
            surf_data = response.json()
            print("Using real API data for surf conditions.")  # Log this when real API data is used

            # Check if response body is empty
            if not response.text.strip():
                return render_template("error.html", message="Empty response from API.")
        else:
            print("API call failed. Switching to mock data.")
            surf_data = mock_response  # Fallback to mock data if API fails
    except Exception as e:
        print(f"Error occurred: {e}. Switching to mock data.")
        surf_data = mock_response  # Use mock data in case of an exception

    # Extract specific data safely
    wave_height = surf_data.get('hours', [{}])[0].get('waveHeight', {}).get('sg', "No data available")
    wind_speed = surf_data.get('hours', [{}])[0].get('windSpeed', {}).get('sg', "No data available")
    wind_direction = surf_data.get('hours', [{}])[0].get('windDirection', {}).get('sg', "No data available")

    # Calculate wind speed in mph
    mph_conversion_factor = 2.237
    wind_speed_mph = round(float(wind_speed) * mph_conversion_factor, 2) if isinstance(wind_speed, (int, float)) else "No data available"

    # Define coastline orientation (example: east-facing coastline)
    coastline_orientation = 90  # Adjust this based on the location
    if isinstance(wind_direction, (int, float)):
        wind_classification = classify_wind_direction(wind_direction, coastline_orientation)
    else:
        wind_classification = "No data available"

    # Generate a surf conditions message dynamically
    if wave_height != "No data available" and float(wave_height) > 1.5:
        surf_message = f"With a wave height of {wave_height} meters, it's an exciting day for experienced surfers!"
    elif float(wave_height) > 1.0:
        surf_message = f"With a wave height of {wave_height} meters, it's a decent day for some fun in the water."
    else:
        surf_message = f"Wave height is {wave_height} meters. It’s a calm day—great for beginners!"

    if wind_classification == "Onshore":
        wind_message = f"The wind speed is {wind_speed_mph} mph with an onshore breeze, which may make the waves a bit choppy."
    elif wind_classification == "Offshore":
        wind_message = f"The wind speed is {wind_speed_mph} mph with an offshore breeze—perfect for creating clean waves!"
    else:
        wind_message = f"The wind speed is {wind_speed_mph} mph, with the wind running parallel to the shore."

    final_message = f"Surf Conditions for {location}:\n{surf_message}\n{wind_message}"
    
    # Pass extracted data and final message to the template
    return render_template(
        "surf_conditions.html",
        location=full_address,  # Show full address provided
        wave_height=wave_height,
        wind_direction=wind_direction,
        wind_speed=wind_speed,
        wind_speed_mph=wind_speed_mph,
        wind_classification=wind_classification,
        final_message=final_message
    )
    

@app.route("/test_geocoding", methods=["GET"])
def test_geocoding():
    try:
        location = geolocator.geocode("Long Beach, Nassau County, New York")
        if location:
            message = f"Latitude: {location.latitude}, Longitude: {location.longitude}"
        else:
            message = "Geocoding failed. Please check your API key or location."
        return render_template("test_geocoding.html", message=message)
    except Exception as e:
        return render_template("test_geocoding.html", message=f"Geocoding error: {str(e)}")


