// Effects display functions
async function updateEffectsWithParams(params) {
    try {
        // Calculate energy based on parameters
        const mass = calculateMass(params.diameter_km);
        const energy = 0.5 * mass * Math.pow(params.velocity_kmh / 3.6, 2); // Convert km/h to m/s
        
        // Create data object similar to API response
        const data = {
            energy: {
                kinetic_energy_j: energy,
                tnt_equivalent_mt: energy / 4.184e15
            },
            crater_effects: {
                crater_diameter_km: Math.pow(energy / 4.184e15, 1/3) * 0.5, // Simple approximation based on energy
                estimated_asteroid_diameter_m: params.diameter_km * 1000
            }
        };
        
        displayEffects(data);
        return data;
    } catch (error) {
        console.error('Error updating effects:', error);
    }
}

// Helper function to calculate mass from diameter
function calculateMass(diameter_km, density = 3000) {
    const radius_m = (diameter_km * 1000) / 2;
    const volume = (4/3) * Math.PI * Math.pow(radius_m, 3);
    return volume * density;
}

async function updateEffectsInfo(lat, lon) {
    try {
        const response = await fetch('/api/impact-effects');
        const data = await response.json();
        displayEffects(data);
    } catch (error) {
        console.error('Error fetching impact effects:', error);
    }
}

function displayEffects(data) {
    const infoDiv = document.getElementById('effects-info');
    const energy = data.energy;
    const effects = data.effects_by_distance;
    
    // Calculate damage radii based on scientific models
    const energyMT = energy.tnt_equivalent_mt;
    
    // Using scaled calculations based on nuclear weapons effects and asteroid impact studies
    // Overpressure levels in kilopascals (kPa)
    // Radius scales with cube root of yield, using Hopkinson-Cranz scaling law
    const zones = [
        { 
            radius: Math.pow(energyMT, 1/3) * 0.35, // Direct calculation in km using Hopkinson-Cranz scaling
            description: "Total Destruction (≥140 kPa)" 
        },
        { 
            radius: Math.pow(energyMT, 1/3) * 0.56,
            description: "Severe Damage (≥70 kPa)" 
        },
        { 
            radius: Math.pow(energyMT, 1/3) * 0.85,
            description: "Moderate Damage (≥35 kPa)" 
        },
        { 
            radius: Math.pow(energyMT, 1/3) * 1.40,
            description: "Light Damage (≥14 kPa)" 
        },
        { 
            radius: Math.pow(energyMT, 1/3) * 2.17,
            description: "Window Breakage (≥7 kPa)" 
        }
    ];
    
    let html = `
        <div class="effect-details">
            <div class="effect-section">
                <label class="title">Impact Details</label>
                <div class="detail-row">
                    <div class="detail-name">Impact Energy</div>
                    <div class="detail-value">${energy.tnt_equivalent_mt.toFixed(2)} Megatons TNT</div>
                </div>
                <div class="detail-row">
                    <div class="detail-name">Energy in Joules</div>
                    <div class="detail-value">${energy.kinetic_energy_j.toExponential(2)} J</div>
                </div>
                <div class="detail-row">
                    <div class="detail-name">Crater Diameter</div>
                    <div class="detail-value">${data.crater_effects ? Math.round(data.crater_effects.crater_diameter_km * 10) / 10 : 'N/A'} km</div>
                </div>
            </div>

            <div class="effect-section">
                <label class="title">Damage Zones</label>
                ${zones.map(zone => `
                    <div class="damage-zone">
                        <div class="zone-name">${zone.description}</div>
                        <div class="zone-radius">${Math.round(zone.radius)} km radius</div>
                    </div>
                `).join('')}
            </div>
            
        </div>
    `;
    
    infoDiv.innerHTML = html;
}
