from flask import Flask, jsonify, request, send_from_directory, render_template
from physics_calculator import AsteroidData, calculate_impact_effects
import json
import os

app = Flask(__name__, static_folder='static')

def load_asteroid_data():
    """Load the specific asteroid data"""
    with open('data/specific_asteroids/asteroid_54131736.json', 'r') as f:
        data = json.load(f)
    return data

def load_meteor_data():
    """Load all meteor data from CSV"""
    import csv
    meteors = []
    with open('data/all_meteors/visualization/processed_meteors.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            meteor = {
                'name': row['name'],
                'diameter_km': (float(row['diameter_min_km']) + float(row['diameter_max_km'])) / 2,
                'velocity_kmh': float(row['relative_velocity_kph']),
                'is_hazardous': row['is_potentially_hazardous'] == 'True',
                'miss_distance_km': float(row['miss_distance_km'])
            }
            meteors.append(meteor)
    return meteors

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/asteroid')
def get_asteroid_data():
    """Get basic asteroid information"""
    data = load_asteroid_data()
    return jsonify(data)

@app.route('/api/meteors')
def get_meteor_data():
    """Get all meteor data"""
    data = load_meteor_data()
    return jsonify(data)

@app.route('/api/impact-effects')
def get_impact_effects():
    """Calculate impact effects based on query parameters"""
    # Get parameters with defaults
    distance = float(request.args.get('distance', 100))  # km
    
    # Load asteroid data
    data = load_asteroid_data()
    close_approach = next(
        (approach for approach in data['close_approach_data'] 
         if approach['close_approach_date'] == '2025-10-06'),
        data['close_approach_data'][0]
    )
    
    # Create asteroid object
    asteroid = AsteroidData(
        diameter=(
            data['estimated_diameter']['kilometers']['estimated_diameter_min'] +
            data['estimated_diameter']['kilometers']['estimated_diameter_max']
        ) / 2,
        velocity=float(close_approach['relative_velocity']['kilometers_per_hour']),
        mass=0,  # Will be calculated based on diameter
        distance=float(close_approach['miss_distance']['kilometers'])
    )
    
    # Calculate effects
    effects = calculate_impact_effects(asteroid)
    return jsonify(effects)

if __name__ == '__main__':
    # Create static directory if it doesn't exist
    os.makedirs('static', exist_ok=True)
    app.run(debug=True)
