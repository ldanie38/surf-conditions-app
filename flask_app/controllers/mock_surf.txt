from flask import render_template, request
from flask_app import app
import requests
import os

# Define the classify_wind_direction function
def classify_wind_direction(wind_direction, coastline_orientation):
    # Calculate the difference between wind direction and coastline orientation
    difference = (wind_direction - coastline_orientation) % 360
    if 45 <= difference <= 135:  # Within 45-135° range
        return "Onshore"
    elif 225 <= difference <= 315:  # Within 225-315° range
        return "Offshore"
    else:
        return "Parallel to Shore"

@app.route('/')
def index():
    return render_template('index.html')

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

    # Mock latitude and longitude for development
    lat, lng = 10.2958, -85.8516  # Example: Playa Grande, Costa Rica
    print(f"Mock Geocoded: lat={lat}, lng={lng}")  # Debugging information

    # Use Mock Data for Surf Conditions
    mock_response = {
        'hours': [
            {'waveHeight': {'sg': 0.95}, 'windDirection': {'sg': 240.33}, 'windSpeed': {'sg': 9.06}}
        ]
    }
    surf_data = mock_response

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
