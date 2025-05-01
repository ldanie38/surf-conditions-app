from flask import render_template, request
from flask_app import app
import requests
from geopy.geocoders import GoogleV3
import os

#  Google Maps API key from environment variables
api_key = os.getenv("GOOGLE_MAPS_API_KEY")  

# Initialize GoogleV3 geolocator with my API key
geolocator = GoogleV3(api_key="AIzaSyCR3oDGLh4JBoSYOZedCAMQh7VY_63jVMw") # gets the coordinates

STORMGLASS_API_KEY = "5444b2d0-1b36-11f0-bda0-0242ac130003-5444b32a-1b36-11f0-bda0-0242ac130003" # gets surf/weather
STORMGLASS_URL = "https://api.stormglass.io/v2/weather/point"

@app.route('/')
def index():
    return render_template('index.html')

def classify_wind_direction(wind_direction, coastline_orientation):
    # Calculate difference between wind direction and coastline orientation
    difference = (wind_direction - coastline_orientation) % 360
    if 45 <= difference <= 135:
        return "Onshore"
    elif 225 <= difference <= 315:
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
        return render_template("error.html", message="Please enter a location.")

    # Combine inputs into a full address for geocoding
    full_address = location
    if country:
        full_address += f", {country}"
    if province:
        full_address += f", {province}"
    
    print(f"Full address for geocoding: {full_address}")

    # Step 1: Geocode the location to get latitude and longitude
    try:
        geolocation = geolocator.geocode(full_address)
        if not geolocation:
            return render_template("error.html", message=f"Could not find '{full_address}'. Try another.")
        lat, lng = geolocation.latitude, geolocation.longitude
        print(f"Geocoded: lat={lat}, lng={lng}")
    except Exception as e:
        return render_template("error.html", message=f"Geocoding error: {str(e)}")

    # Step 2: Fetch surf conditions from the Stormglass API
    headers = {"Authorization": STORMGLASS_API_KEY}
    print("Headers:", headers) 
    params = {
        "lat": lat,
        "lng": lng,
        "params": "waveHeight,windSpeed,windDirection,airTemperature,precipitation,seaLevel",
        "source": "sg"  # Primary source
    }

    # Mock Data for Development

    mock_response = {
    'hours': [
        {'waveHeight': {'sg': 0.95}, 
         'windDirection': {'sg': 240.33}, 
         'windSpeed': {'sg': 9.06},'airTemperature': {'sg': 18.5},'precipitation': {'sg': 0.2},
         'seaLevel': {'sg': 1.8}}
    ]
    
    }
    

    try:
        response = requests.get(STORMGLASS_URL, params=params, headers=headers)
        # Debugging: Print response details
        print("API Response Status Code:", response.status_code)
        print("API Response Text:", response.text)
        if response.status_code == 200:
            surf_data = response.json()
            print("Using real API data for surf conditions.")
            if not response.text.strip():
                return render_template("error.html", message="Empty response from API.")
        else:
            print("API call failed. Switching to mock data.")
            surf_data = mock_response
    except Exception as e:
        print(f"Error occurred: {e}. Switching to mock data.")
        surf_data = mock_response
    # **DEBUGGING STEP: Print API response**
    print("Stormglass API response:", surf_data)  

    # Extract specific data safely
    wave_height = surf_data.get('hours', [{}])[0].get('waveHeight', {}).get('sg', "No data available")
    wind_speed = surf_data.get('hours', [{}])[0].get('windSpeed', {}).get('sg', "No data available")
    wind_direction = surf_data.get('hours', [{}])[0].get('windDirection', {}).get('sg', "No data available")
    precipitation = surf_data.get('hours', [{}])[0].get('precipitation', {}).get('sg', "No data available")
    air_temperature = surf_data.get('hours', [{}])[0].get('airTemperature', {}).get('sg')
    tide_height = surf_data.get('hours', [{}])[0].get('seaLevel', {}).get('sg', "No data available")

    #air_temp
    if air_temperature is not None and isinstance(air_temperature, (int, float)):
        air_temperature_f = round((float(air_temperature) * 9/5) + 32, 2)
    else:
        air_temperature_f = "No data available"

    print("Converted air temperature (°F):", air_temperature_f)
    
    #precipitation
    if precipitation != "No data available":
        precipitation_val = float(precipitation)
        # Define thresholds for a simple chance-of-rain estimate:
        # This logic is arbitrary and should be calibrated based on your needs.
        if precipitation_val == 0:
            chance_of_rain = 0
        elif precipitation_val < 0.1:
            chance_of_rain = 10
        elif precipitation_val < 1:
            chance_of_rain = 50
        else:
            chance_of_rain = 90
        rain_message = f"There is roughly a {chance_of_rain}% chance of rain."
    else:
        rain_message = "Precipitation data is not available."
        

    # Convert wave height from meters to feet if data is available
    if wave_height != "No data available":
        wave_height_m = float(wave_height)
        wave_height_ft = round(wave_height_m * 3.28084, 2)
    else:
        wave_height_ft = "No data available"

    # Calculate wind speed in mph (conversion factor: 1 m/s ≈ 2.237 mph)
    mph_conversion_factor = 2.237
    wind_speed_mph = round(float(wind_speed) * mph_conversion_factor, 2) if isinstance(wind_speed, (int, float)) else "No data available"

    # Define coastline orientation (example: east-facing coastline with angle 90°)
    coastline_orientation = 90
    if isinstance(wind_direction, (int, float)):
        wind_classification = classify_wind_direction(wind_direction, coastline_orientation)
    else:
        wind_classification = "No data available"

    # Generate a surf conditions message using the wave height in feet
    if wave_height != "No data available" and float(wave_height) > 1.5:
        surf_message = f"With a wave height of {wave_height_ft} feet, it's an exciting day for experienced surfers!"
    elif wave_height != "No data available" and float(wave_height) > 1.0:
        surf_message = f"With a wave height of {wave_height_ft} feet, it's a decent day for some fun in the water."
    elif wave_height != "No data available":
        surf_message = f"Wave height is {wave_height_ft} feet. It’s a calm day—great for beginners!"
    else:
        surf_message = "Wave height data is not available."

    if wind_classification == "Onshore":
        wind_message = f"The wind speed is {wind_speed_mph} mph with an onshore breeze, which may make the waves a bit choppy."
    elif wind_classification == "Offshore":
        wind_message = f"The wind speed is {wind_speed_mph} mph with an offshore breeze—perfect for creating clean waves!"
    else:
        wind_message = f"The wind speed is {wind_speed_mph} mph, with the wind running parallel to the shore."

    final_message = f"Surf Conditions for {location}:\n{surf_message}\n{wind_message}"
    
    ##Classify High Tide vs. Low Tide
    if tide_height != "No data available":
        tide_value = float(tide_height)
    
    if tide_height != "No data available":
        tide_value = float(tide_height)
        
        # Define basic tide thresholds (These should be adjusted based on local tide patterns)
        if tide_value > 1.5:
            tide_status = "High Tide"
        elif tide_value < 0.5:
            tide_status = "Low Tide"
        else:
            tide_status = "Mid Tide"

        tide_message = f"The current tide level is {tide_value} meters, classified as {tide_status}."
    else:
        tide_message = "Tide data is not available."

    
    return render_template(
        "surf_conditions.html",
        location=full_address,
        wave_height=wave_height_ft,
        wind_direction=wind_direction,
        wind_speed=wind_speed,
        wind_speed_mph=wind_speed_mph,
        wind_classification=wind_classification,
        air_temperature_f=air_temperature_f, 
        rain_message=rain_message,
        tide_message=tide_message, 
        final_message=final_message,
        lat=lat,
        lng=lng
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
