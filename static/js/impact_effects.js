// Simple impact visualization
let impactMarker = null;

function createImpactPoint(lat, lon) {
    // Convert lat/lon to 3D position on Earth's surface
    const phi = (90 - lat) * (Math.PI / 180);
    const theta = (lon + 180) * (Math.PI / 180);
    
    const x = -(EARTH_RADIUS * Math.sin(phi) * Math.cos(theta));
    const z = (EARTH_RADIUS * Math.sin(phi) * Math.sin(theta));
    const y = (EARTH_RADIUS * Math.cos(phi));
    
    return new THREE.Vector3(x, y, z);
}

function createDamageCircles(baseRadius, craterRadius) {
    const group = new THREE.Group();
    
    // Add crater visualization first
    if (craterRadius) {
        const craterGeometry = new THREE.CircleGeometry(craterRadius, 64);
        const craterMaterial = new THREE.MeshBasicMaterial({
            color: 0x8B4513,  // Saddle Brown - representing crater
            opacity: 0.95,
            transparent: true,
            side: THREE.DoubleSide,
            depthWrite: false
        });
        const crater = new THREE.Mesh(craterGeometry, craterMaterial);
        group.add(crater);
    }
    
    // Define zones based on real damage effects
    const zones = [
        { radius: baseRadius * 1, color: 0xff69b4, opacity: 0.9 },  // Hot Pink - Total destruction
        { radius: baseRadius * 2, color: 0xff1493, opacity: 0.8 },  // Deep Pink - Severe damage
        { radius: baseRadius * 4, color: 0xff0000, opacity: 0.7 },  // Red - Moderate damage
        { radius: baseRadius * 8, color: 0xff4500, opacity: 0.5 },  // Orange Red - Light damage
        { radius: baseRadius * 16, color: 0xffa500, opacity: 0.3 }  // Orange - Window breakage
    ];
    
    zones.forEach((zone, index) => {
        // Create a ring (difference between outer and inner circle)
        const innerRadius = index > 0 ? zones[index - 1].radius : 0;
        const geometry = new THREE.RingGeometry(innerRadius, zone.radius, 64);
        const material = new THREE.MeshBasicMaterial({
            color: zone.color,
            opacity: zone.opacity,
            transparent: true,
            side: THREE.DoubleSide,
            depthWrite: false,
            polygonOffset: true,
            polygonOffsetFactor: -1,
            polygonOffsetUnits: -1
        });
        const ring = new THREE.Mesh(geometry, material);
        group.add(ring);
    });
    
    return group;
}

function updateDamageZones(position, baseRadius, craterRadius) {
    // Remove existing marker if any
    if (impactMarker) {
        scene.remove(impactMarker);
    }
    
    // Create new impact marker group
    impactMarker = new THREE.Group();
    
    // Create damage circles with crater
    const circles = createDamageCircles(baseRadius, craterRadius);
    impactMarker.add(circles);
    
    // Position circles well above surface to prevent z-fighting
    const surfaceOffset = 200; // Increased to 200 km
    const direction = position.clone().normalize();
    const surfacePosition = direction.multiplyScalar(EARTH_RADIUS + surfaceOffset);
    impactMarker.position.copy(surfacePosition);
    
    // Orient circles to stand up vertically from the surface
    impactMarker.lookAt(new THREE.Vector3(0, 0, 0));
    
    scene.add(impactMarker);
}

async function createDamageZones(position) {
    try {
        // Get initial values from sliders
        const diameter = parseFloat(document.getElementById('diameter-slider').value);
        const velocity = parseFloat(document.getElementById('velocity-slider').value) * 3600;
        
        // Calculate initial impact data
        const impactData = {
            diameter_km: diameter,
            velocity_kmh: velocity
        };
        
        // Get effects data
        const data = await updateEffectsWithParams(impactData);
        const baseRadius = Math.pow(data.energy.tnt_equivalent_mt, 1/3) * 10;
        const craterRadius = data.crater_effects.crater_diameter_km * 10;  // Scale crater size for visualization
        
        // Create initial damage zones
        updateDamageZones(position, baseRadius, craterRadius);
        
    } catch (error) {
        console.error('Error creating damage zones:', error);
    }
}

// Add click handler to Earth
function addEarthClickHandler() {
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();
    
    document.getElementById('visualization').addEventListener('click', (event) => {
        // Calculate mouse position in normalized device coordinates
        const rect = event.target.getBoundingClientRect();
        mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
        
        raycaster.setFromCamera(mouse, camera);
        const intersects = raycaster.intersectObject(earth);
        
        if (intersects.length > 0) {
            const point = intersects[0].point;
            // Convert to lat/lon
            const lat = 90 - (Math.acos(point.y / EARTH_RADIUS) * 180 / Math.PI);
            const lon = (Math.atan2(point.z, -point.x) * 180 / Math.PI);
            
            // Create damage zones at clicked position
            createDamageZones(point);
            
            console.log(`Impact at lat: ${lat.toFixed(2)}, lon: ${lon.toFixed(2)}`);
        }
    });
}

// Initialize with crosshair cursor
document.getElementById('visualization').style.cursor = 'crosshair';