import numpy as np
from dataclasses import dataclass
from typing import Dict, Tuple

@dataclass
class AsteroidData:
    """Class to hold asteroid physical properties"""
    diameter: float  # km
    velocity: float  # km/h
    mass: float     # kg
    distance: float # km

def calculate_mass(diameter_km: float, density: float = 3000) -> float:
    """
    Calculate asteroid mass assuming spherical shape
    Args:
        diameter_km: Diameter in kilometers
        density: Density in kg/m³ (default 3000 kg/m³ - typical asteroid density)
    Returns:
        Mass in kg
    """
    radius_m = (diameter_km * 1000) / 2
    volume = (4/3) * np.pi * (radius_m ** 3)
    return volume * density

def calculate_kinetic_energy(mass: float, velocity: float) -> float:
    """
    Calculate kinetic energy
    Args:
        mass: Mass in kg
        velocity: Velocity in km/h
    Returns:
        Energy in Joules
    """
    # Convert km/h to m/s
    velocity_ms = velocity * (1000 / 3600)
    return 0.5 * mass * (velocity_ms ** 2)

def calculate_tnt_equivalent(energy: float) -> float:
    """
    Convert energy to TNT equivalent in megatons
    Args:
        energy: Energy in Joules
    Returns:
        TNT equivalent in megatons
    """
    # 1 megaton TNT = 4.184e15 Joules
    return energy / 4.184e15

def calculate_air_burst_effects(energy: float, distance_km: float) -> Dict[str, float]:
    """
    Calculate effects of airburst at given distance
    Args:
        energy: Energy in Joules
        distance_km: Distance from burst in kilometers
    Returns:
        Dictionary of effects and their values
    """
    distance_m = distance_km * 1000
    energy_mt = calculate_tnt_equivalent(energy)
    
    # Simplified scaling laws based on nuclear weapons effects
    # (scaled for asteroid impacts)
    
    # Pressure wave (overpressure in kPa)
    pressure = 100 * (energy_mt ** (1/3)) / distance_m
    
    # Thermal radiation (in kW/m²)
    thermal = 1000 * energy_mt / (4 * np.pi * (distance_m ** 2))
    
    return {
        "overpressure_kpa": pressure,
        "thermal_radiation_kw_m2": thermal,
        "damage_radius_km": 0.28 * (energy_mt ** (1/3))  # Approximate radius of severe damage
    }

def calculate_gravitational_effects(mass: float, distance_km: float) -> Dict[str, float]:
    """
    Calculate gravitational effects at closest approach
    Args:
        mass: Mass in kg
        distance_km: Distance in kilometers
    Returns:
        Dictionary of gravitational effects
    """
    G = 6.67430e-11  # gravitational constant
    earth_mass = 5.972e24  # kg
    distance_m = distance_km * 1000
    
    force = G * mass * earth_mass / (distance_m ** 2)
    
    # Tidal force (approximate)
    tidal_force = 2 * G * mass * earth_mass * earth_mass / (distance_m ** 3)
    
    return {
        "gravitational_force_n": force,
        "tidal_force_n": tidal_force
    }

def calculate_impact_effects(asteroid: AsteroidData) -> Dict[str, Dict[str, float]]:
    """
    Calculate comprehensive impact effects
    Args:
        asteroid: AsteroidData object with asteroid properties
    Returns:
        Dictionary of various effects and their values
    """
    # Calculate mass if not provided
    if asteroid.mass <= 0:
        asteroid.mass = calculate_mass(asteroid.diameter)
    
    # Calculate energy
    kinetic_energy = calculate_kinetic_energy(asteroid.mass, asteroid.velocity)
    tnt_equivalent = calculate_tnt_equivalent(kinetic_energy)
    
    # Calculate effects at various distances
    distances = [10, 50, 100, 500, 1000]  # km
    effects_by_distance = {}
    
    for dist in distances:
        effects = calculate_air_burst_effects(kinetic_energy, dist)
        effects_by_distance[str(dist)] = effects
    
    # Calculate gravitational effects at closest approach
    grav_effects = calculate_gravitational_effects(asteroid.mass, asteroid.distance)
    
    return {
        "energy": {
            "kinetic_energy_j": kinetic_energy,
            "tnt_equivalent_mt": tnt_equivalent
        },
        "effects_by_distance": effects_by_distance,
        "gravitational_effects": grav_effects,
        "asteroid_properties": {
            "mass_kg": asteroid.mass,
            "diameter_km": asteroid.diameter,
            "velocity_kmh": asteroid.velocity,
            "distance_km": asteroid.distance
        }
    }

def get_damage_description(pressure: float) -> str:
    """
    Get description of damage based on overpressure
    Args:
        pressure: Overpressure in kPa
    Returns:
        Description of damage
    """
    if pressure > 200:
        return "Complete destruction of buildings"
    elif pressure > 100:
        return "Severe damage to reinforced concrete buildings"
    elif pressure > 50:
        return "Most buildings collapse"
    elif pressure > 30:
        return "Unreinforced buildings collapse"
    elif pressure > 10:
        return "Residential buildings severely damaged"
    elif pressure > 5:
        return "Windows shatter, light building damage"
    else:
        return "Minor damage"
