from flask import render_template, request
from flask_app import app
import requests
from geopy.geocoders import Nominatim

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
    location = request.form.get("location")  # Retrieve user-provided location
    
    if not location: 
        return render_template("error.html", message="Please enter a location.")  # Handle empty location input
    
    # Step 1: Geocode the location to get latitude and longitude
    geolocator = Nominatim(user_agent="surf_app")
    try:
        geolocation = geolocator.geocode(location)
        
        if not geolocation:  # Handle invalid or unrecognized locations
            return render_template("error.html", message=f"Could not find '{location}'. Try another.")
        
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

    try:
        response = requests.get(STORMGLASS_URL, params=params, headers=headers)
        print(response.json())  # Debugging: Print the full API response
        
        if response.status_code == 200:
            surf_data = response.json()
            
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

            # Pass extracted data to the template
            return render_template(
                "surf_conditions.html", 
                location=location, 
                wave_height=wave_height,
                wind_direction=wind_direction,
                wind_speed=wind_speed,
                wind_speed_mph=wind_speed_mph,
                wind_classification=wind_classification
            )
        else:
            print(f"API response: {response.json()}")  # Debugging the response
            return render_template("error.html", message="Failed to fetch surf data.")
    except Exception as e:
        print(f"API error: {str(e)}")  # Debugging the error
        return render_template("error.html", message=f"API error: {str(e)}")
