import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

def load_asteroid_data(asteroid_id):
    """Load the asteroid data from JSON file"""
    filepath = f'data/specific_asteroids/asteroid_{asteroid_id}.json'
    with open(filepath, 'r') as f:
        return json.load(f)

def create_approaches_dataframe(data):
    """Convert close approaches data to DataFrame"""
    approaches = []
    
    for approach in data['close_approach_data']:
        approach_data = {
            'date': datetime.strptime(approach['close_approach_date'], '%Y-%m-%d'),
            'velocity_kph': float(approach['relative_velocity']['kilometers_per_hour']),
            'miss_distance_km': float(approach['miss_distance']['kilometers']),
            'orbiting_body': approach['orbiting_body']
        }
        approaches.append(approach_data)
    
    df = pd.DataFrame(approaches)
    
    # Save to CSV
    os.makedirs('data/specific_asteroids', exist_ok=True)
    csv_path = f'data/specific_asteroids/asteroid_{ASTEROID_ID}_approaches.csv'
    df.to_csv(csv_path, index=False)
    print(f"Approach data saved to {csv_path}")
    
    return df

def plot_miss_distance_timeline(df):
    """Create timeline of miss distances"""
    plt.figure(figsize=(12, 6))
    plt.plot(df['date'], df['miss_distance_km'] / 1000, marker='o')
    
    # Highlight the October 2025 approach
    oct_2025 = df[df['date'].dt.strftime('%Y-%m-%d') == '2025-10-06']
    if not oct_2025.empty:
        plt.scatter(oct_2025['date'], oct_2025['miss_distance_km'] / 1000, 
                   color='red', s=100, zorder=5, label='October 2025 Approach')
    
    plt.title('Miss Distance Timeline')
    plt.xlabel('Date')
    plt.ylabel('Miss Distance (thousand km)')
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.legend()
    
    save_path = 'data/specific_asteroids/visualization'
    os.makedirs(save_path, exist_ok=True)
    plt.savefig(f'{save_path}/miss_distance_timeline.png', bbox_inches='tight')
    plt.close()

def plot_velocity_vs_distance(df):
    """Create scatter plot of velocity vs miss distance"""
    plt.figure(figsize=(10, 6))
    plt.scatter(df['velocity_kph'] / 1000, df['miss_distance_km'] / 1000)
    
    # Highlight the October 2025 approach
    oct_2025 = df[df['date'].dt.strftime('%Y-%m-%d') == '2025-10-06']
    if not oct_2025.empty:
        plt.scatter(oct_2025['velocity_kph'] / 1000, oct_2025['miss_distance_km'] / 1000,
                   color='red', s=100, zorder=5, label='October 2025 Approach')
    
    plt.title('Velocity vs Miss Distance')
    plt.xlabel('Velocity (thousand km/h)')
    plt.ylabel('Miss Distance (thousand km)')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    save_path = 'data/specific_asteroids/visualization'
    plt.savefig(f'{save_path}/velocity_vs_distance.png', bbox_inches='tight')
    plt.close()

def plot_approaches_by_year(df):
    """Create histogram of approaches by year"""
    plt.figure(figsize=(12, 6))
    df['year'] = df['date'].dt.year
    year_counts = df['year'].value_counts().sort_index()
    
    plt.bar(year_counts.index, year_counts.values)
    plt.title('Number of Close Approaches by Year')
    plt.xlabel('Year')
    plt.ylabel('Number of Approaches')
    plt.grid(True, alpha=0.3)
    
    save_path = 'data/specific_asteroids/visualization'
    plt.savefig(f'{save_path}/approaches_by_year.png', bbox_inches='tight')
    plt.close()

def create_summary_file(data, df):
    """Create a text file with summary statistics"""
    save_path = 'data/specific_asteroids/visualization'
    with open(f'{save_path}/asteroid_summary.txt', 'w') as f:
        f.write(f"Asteroid {data['name']} Summary\n")
        f.write("=" * 40 + "\n\n")
        
        # Basic information
        f.write("Basic Information:\n")
        f.write(f"NASA JPL URL: {data['nasa_jpl_url']}\n")
        f.write(f"Absolute Magnitude (H): {data['absolute_magnitude_h']}\n")
        
        # Size information
        diameter_km = data['estimated_diameter']['kilometers']
        f.write("\nSize Estimates:\n")
        f.write(f"Minimum Diameter: {diameter_km['estimated_diameter_min']:.2f} km\n")
        f.write(f"Maximum Diameter: {diameter_km['estimated_diameter_max']:.2f} km\n")
        
        # Approach statistics
        f.write("\nClose Approach Statistics:\n")
        f.write(f"Total number of known approaches: {len(df)}\n")
        f.write(f"Closest approach distance: {df['miss_distance_km'].min():,.2f} km\n")
        f.write(f"Average miss distance: {df['miss_distance_km'].mean():,.2f} km\n")
        f.write(f"Maximum relative velocity: {df['velocity_kph'].max():,.2f} km/h\n")
        f.write(f"Average relative velocity: {df['velocity_kph'].mean():,.2f} km/h\n")
        
        # October 2025 approach details
        oct_2025 = df[df['date'].dt.strftime('%Y-%m-%d') == '2025-10-06']
        if not oct_2025.empty:
            f.write("\nOctober 2025 Approach Details:\n")
            f.write(f"Miss Distance: {oct_2025['miss_distance_km'].iloc[0]:,.2f} km\n")
            f.write(f"Relative Velocity: {oct_2025['velocity_kph'].iloc[0]:,.2f} km/h\n")

def main():
    global ASTEROID_ID
    ASTEROID_ID = '54131736'
    
    # Load the asteroid data
    print(f"Processing data for asteroid {ASTEROID_ID}...")
    data = load_asteroid_data(ASTEROID_ID)
    
    # Create DataFrame of close approaches
    df = create_approaches_dataframe(data)
    
    # Create visualizations directory
    os.makedirs('data/specific_asteroids/visualization', exist_ok=True)
    
    # Generate visualizations
    print("Creating visualizations...")
    plot_miss_distance_timeline(df)
    plot_velocity_vs_distance(df)
    plot_approaches_by_year(df)
    
    # Create summary file
    create_summary_file(data, df)
    
    print("\nFiles created in data/specific_asteroids/:")
    print("- asteroid_54131736_approaches.csv")
    print("- visualization/miss_distance_timeline.png")
    print("- visualization/velocity_vs_distance.png")
    print("- visualization/approaches_by_year.png")
    print("- visualization/asteroid_summary.txt")

if __name__ == "__main__":
    main()
