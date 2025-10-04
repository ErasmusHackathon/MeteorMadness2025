import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# NASA API configuration
NASA_API_KEY = os.getenv('NASA_API_KEY')
if not NASA_API_KEY:
    raise ValueError("NASA_API_KEY not found in environment variables. Please check your .env file.")

def fetch_asteroid_details(asteroid_id):
    """
    Fetch detailed information about a specific asteroid using its NASA JPL small body ID
    """
    BASE_URL = f'https://api.nasa.gov/neo/rest/v1/neo/{asteroid_id}'
    
    params = {
        'api_key': NASA_API_KEY
    }
    
    try:
        print(f"Fetching detailed data for asteroid ID: {asteroid_id}")
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def analyze_close_approaches(data):
    """Analyze and display close approach data"""
    approaches = data['close_approach_data']
    
    # Sort approaches by date
    approaches.sort(key=lambda x: x['close_approach_date'])
    
    print("\nClose Approaches Analysis:")
    print("==========================")
    
    for approach in approaches:
        date = approach['close_approach_date']
        velocity_kph = float(approach['relative_velocity']['kilometers_per_hour'])
        miss_distance_km = float(approach['miss_distance']['kilometers'])
        
        print(f"\nDate: {date}")
        print(f"Relative Velocity: {velocity_kph:,.2f} km/h")
        print(f"Miss Distance: {miss_distance_km:,.2f} km")
        print(f"Orbiting Body: {approach['orbiting_body']}")

def save_asteroid_data(data, asteroid_id):
    """Save the asteroid data to a JSON file"""
    os.makedirs('data/specific_asteroids', exist_ok=True)
    filename = f'data/specific_asteroids/asteroid_{asteroid_id}.json'
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"\nRaw data saved to {filename}")

def main():
    # Asteroid ID we're interested in
    ASTEROID_ID = '54131736'
    
    # Fetch the data
    data = fetch_asteroid_details(ASTEROID_ID)
    
    if data:
        # Save raw data
        save_asteroid_data(data, ASTEROID_ID)
        
        # Print basic information
        print("\nAsteroid Information:")
        print("=====================")
        print(f"Name: {data['name']}")
        print(f"NASA JPL URL: {data['nasa_jpl_url']}")
        print(f"Absolute Magnitude (H): {data['absolute_magnitude_h']}")
        
        # Diameter information
        diameter_km = data['estimated_diameter']['kilometers']
        print(f"\nEstimated Diameter:")
        print(f"Minimum: {diameter_km['estimated_diameter_min']:.2f} km")
        print(f"Maximum: {diameter_km['estimated_diameter_max']:.2f} km")
        
        # Hazard information
        print(f"\nPotentially Hazardous: {data['is_potentially_hazardous_asteroid']}")
        print(f"Sentry Object: {data['is_sentry_object']}")
        
        # Orbital data
        orbit = data['orbital_data']
        print(f"\nOrbital Information:")
        print(f"Orbit ID: {orbit['orbit_id']}")
        print(f"First Observation: {orbit['first_observation_date']}")
        print(f"Last Observation: {orbit['last_observation_date']}")
        print(f"Orbit Class: {orbit['orbit_class']['orbit_class_description']}")
        
        # Analyze close approaches
        analyze_close_approaches(data)

if __name__ == "__main__":
    main()
