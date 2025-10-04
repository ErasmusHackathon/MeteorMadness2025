// Load and process meteor data
let meteorData = null;

async function loadMeteorData() {
    try {
        const response = await fetch('/api/meteors');
        const data = await response.json();
        
        // Process the data into a more usable format
        meteorData = data
            .map(meteor => ({
                name: meteor.name,
                diameter: meteor.diameter_km,
                velocity: meteor.velocity_kmh / 3600, // Convert km/h to km/s
                isHazardous: meteor.is_hazardous,
                missDistance: meteor.miss_distance_km
            }))
            .sort((a, b) => b.diameter - a.diameter); // Sort by size, largest first
        
        // Populate the select dropdown
        populateMeteorSelect();
    } catch (error) {
        console.error('Error loading meteor data:', error);
    }
}

function populateMeteorSelect() {
    const select = document.getElementById('meteor-select');
    if (!select || !meteorData) return;
    
    // Add custom option
    select.innerHTML = '<option value="custom">Custom Values</option>';
    
    // Add real meteors
    meteorData.forEach((meteor, index) => {
        const option = document.createElement('option');
        option.value = index;
        const hazardText = meteor.isHazardous ? 'Hazardous' : '';
        option.textContent = `${meteor.name} (${meteor.diameter.toFixed(2)} km, ${meteor.velocity.toFixed(1)} km/s) ${hazardText}`;
        select.appendChild(option);
    });
}

function displayMeteorDetails(meteor) {
    const detailsDiv = document.querySelector('.meteor-info-panel');
    const hazardClass = meteor.isHazardous ? 'text-danger' : '';
    const hazardText = meteor.isHazardous ? 'Yes' : 'No';
    
    const html = `
        <div class="meteor-detail">
            <div class="meteor-section">
                <label class="title">Meteor Properties</label>
                <div class="detail-row">
                    <div class="detail-name">${meteor.name}</div>
                    <div class="detail-value">Asteroid ID</div>
                </div>
                <div class="detail-row">
                    <div class="detail-name">${meteor.diameter.toFixed(3)} kilometers</div>
                    <div class="detail-value">Estimated Diameter</div>
                </div>
                <div class="detail-row">
                    <div class="detail-name">${meteor.velocity.toFixed(1)} km/s</div>
                    <div class="detail-value">Relative Velocity</div>
                </div>
            </div>
            
            <div class="meteor-section">
                <label class="title">Approach Details</label>
                <div class="detail-row">
                    <div class="detail-name">${(meteor.missDistance / 1000).toFixed(0)} thousand km</div>
                    <div class="detail-value">Miss Distance</div>
                </div>
                <div class="detail-row">
                    <div class="detail-name ${hazardClass}">${hazardText}</div>
                    <div class="detail-value">Potentially Hazardous</div>
                </div>
            </div>
        </div>
    `;
    
    detailsDiv.innerHTML = html;
}

function onMeteorSelect(event) {
    const selectedValue = event.target.value;
    const customControls = document.getElementById('custom-controls');
    const meteorDetails = document.getElementById('meteor-details');
    const diameterSlider = document.getElementById('diameter-slider');
    const velocitySlider = document.getElementById('velocity-slider');
    
    if (selectedValue === 'custom') {
        // Show sliders, hide details
        customControls.style.display = 'block';
        meteorDetails.style.display = 'none';
        
        // Enable sliders
        diameterSlider.disabled = false;
        velocitySlider.disabled = false;
        return;
    }
    
    // Get selected meteor data
    const meteor = meteorData[parseInt(selectedValue)];
    if (!meteor) return;
    
    // Hide sliders, show details
    customControls.style.display = 'none';
    meteorDetails.style.display = 'block';
    
    // Display meteor details
    displayMeteorDetails(meteor);
    
    // Update sliders in background (for simulation)
    diameterSlider.value = meteor.diameter;
    velocitySlider.value = meteor.velocity;
    
    // Update simulation
    updateSimulation();
}

// Load meteor data when the page loads
document.addEventListener('DOMContentLoaded', loadMeteorData);
