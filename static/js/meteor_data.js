// Load and process meteor data
let meteorData = null;

function formatYear(year) {
    const currentYear = new Date().getFullYear();
    
    // For recent events (last 2000 years), show the actual year
    if (year > currentYear - 2000) {
        if (year < 0) {
            return `${Math.abs(year)} BCE`;
        }
        return `Year ${year} CE`;
    }
    
    // For ancient events, show "X million/thousand years ago"
    const yearsAgo = currentYear - year;
    if (yearsAgo >= 1000000) {
        return `${(yearsAgo / 1000000).toFixed(1)} million years ago`;
    } else if (yearsAgo >= 1000) {
        return `${(yearsAgo / 1000).toFixed(1)} thousand years ago`;
    }
    return `${yearsAgo} years ago`;
}

async function loadMeteorData() {
    try {
        console.log('Fetching meteor data...');
        const response = await fetch('/static/data/all_meteors/famous_meteors.csv');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const text = await response.text();
        console.log('Received CSV data:', text.slice(0, 100) + '...');
        
        // Parse CSV
        const lines = text.split('\n');
        if (lines.length < 2) {
            throw new Error('CSV file is empty or malformed');
        }
        
        const headers = lines[0].split(',');
        console.log('CSV Headers:', headers);
        
        // Process the data into a more usable format
        meteorData = lines.slice(1)  // Skip header row
            .filter(line => line.trim())  // Skip empty lines
            .map((line, index) => {
                console.log(`Processing line ${index + 1}:`, line);
                const values = line.split(',');
                const meteor = {
                    name: values[0],
                    year: parseInt(values[1]),
                    location: values[2],
                    diameter: parseFloat(values[3]),  // Already in km
                    velocity: parseFloat(values[4]) / 3600,  // Convert km/h to km/s
                    energy: parseFloat(values[5]),  // In megatons TNT
                    craterDiameter: parseFloat(values[6]),  // in km
                    description: values[7]
                };
                console.log('Processed meteor:', meteor);
                return meteor;
            })
            .sort((a, b) => b.diameter - a.diameter);  // Sort by size, largest first
            
        console.log('Processed meteor data:', meteorData);
        
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
    
    // Add historical meteors
    meteorData.forEach((meteor, index) => {
        const option = document.createElement('option');
        option.value = index;
        
        // Format year for readability
        const formattedYear = formatYear(meteor.year);
        
        // Create descriptive text
        option.textContent = `${meteor.name} (${formattedYear}) - ${meteor.location}`;
        
        // Add tooltip with more details
        option.title = `${meteor.name}: ${meteor.description}`;
        
        select.appendChild(option);
    });
}

function displayMeteorDetails(meteor) {
    const detailsDiv = document.querySelector('.meteor-info-panel');
    
    const html = `
        <div class="meteor-detail">
            <div class="meteor-section">
                <label class="title">Historical Impact</label>
                <div class="detail-row">
                    <div class="detail-name">${meteor.name}</div>
                    <div class="detail-value">${formatYear(meteor.year)}</div>
                </div>
                <div class="detail-row">
                    <div class="detail-name">${meteor.location}</div>
                    <div class="detail-value">Location</div>
                </div>
            </div>
            
            <div class="meteor-section">
                <label class="title">Impact Properties</label>
                <div class="detail-row">
                    <div class="detail-name">${meteor.diameter.toFixed(3)} kilometers</div>
                    <div class="detail-value">Estimated Diameter</div>
                </div>
                <div class="detail-row">
                    <div class="detail-name">${meteor.velocity.toFixed(1)} km/s</div>
                    <div class="detail-value">Impact Velocity</div>
                </div>
            </div>

            <div class="meteor-section description-section">
                <label class="title">Historical Significance</label>
                <div class="detail-description">${meteor.description}</div>
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
