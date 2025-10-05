// Update simulation with current values
async function updateSimulation() {
    if (!impactMarker) return; // Only update if there's an impact point
    
    const diameterSlider = document.getElementById('diameter-slider');
    const velocitySlider = document.getElementById('velocity-slider');
    
    const diameter = parseFloat(diameterSlider.value);
    const velocity = parseFloat(velocitySlider.value) * 3600; // Convert km/s to km/h
    
    try {
        // Create custom impact data
        const impactData = {
            diameter_km: diameter,
            velocity_kmh: velocity
        };
        
        // Update effects display with custom parameters
        const data = await updateEffectsWithParams(impactData);
        
        // Update visualization circles
        const baseRadius = Math.pow(data.energy.tnt_equivalent_mt, 1/3) * 10;
        updateDamageZones(impactMarker.position, baseRadius);
        
    } catch (error) {
        console.error('Error updating simulation:', error);
    }
}

// Update value displays and trigger simulation update
function updateValueDisplay(slider) {
    const display = slider.parentElement.querySelector('.value-display');
    const value = parseFloat(slider.value);
    
    if (slider.id === 'diameter-slider') {
        display.textContent = `${value.toFixed(2)} km`;
    } else if (slider.id === 'velocity-slider') {
        display.textContent = `${value} km/s`;
    }
    
    // Update simulation immediately
    updateSimulation();
}

// Initialize controls when the page loads
document.addEventListener('DOMContentLoaded', function() {
    const diameterSlider = document.getElementById('diameter-slider');
    const velocitySlider = document.getElementById('velocity-slider');
    
    // Add input event listeners to sliders
    diameterSlider.addEventListener('input', () => updateValueDisplay(diameterSlider));
    velocitySlider.addEventListener('input', () => updateValueDisplay(velocitySlider));
});