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
    
    // Calculate damage radii based on energy
    const energyMT = energy.tnt_equivalent_mt;
    const baseRadius = Math.pow(energyMT, 1/3) * 10;
    
    const zones = [
        { radius: baseRadius * 1, description: "Total Destruction" },
        { radius: baseRadius * 2, description: "Severe Damage" },
        { radius: baseRadius * 4, description: "Moderate Damage" },
        { radius: baseRadius * 8, description: "Light Damage" },
        { radius: baseRadius * 16, description: "Window Breakage" }
    ];
    
    let html = `
        <div class="effect-details">
            <div class="effect-section">
                <label class="title">Impact Energy</label>
                <div class="effect-value">${energy.tnt_equivalent_mt.toFixed(2)} Megatons TNT</div>
                <div class="effect-subvalue">${energy.kinetic_energy_j.toExponential(2)} Joules</div>
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
