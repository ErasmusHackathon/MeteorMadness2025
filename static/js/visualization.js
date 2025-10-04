// Three.js visualization
let scene, camera, renderer, earth;

// Earth constants
const EARTH_RADIUS = 6371; // km

// Earth texture options
const EARTH_TEXTURES = {
    default: {
        map: 'https://raw.githubusercontent.com/mrdoob/three.js/master/examples/textures/planets/earth_atmos_2048.jpg',
        bump: 'https://raw.githubusercontent.com/mrdoob/three.js/master/examples/textures/planets/earth_normal_2048.jpg'
    }
};

// Current texture set
const currentTexture = EARTH_TEXTURES.default;

// Initialize the scene
function init() {
    // Create scene
    scene = new THREE.Scene();
    
    // Create camera
    camera = new THREE.PerspectiveCamera(
        45,
        document.getElementById('visualization').offsetWidth / document.getElementById('visualization').offsetHeight,
        1,
        1000000
    );
    camera.position.set(0, 15000, 30000);
    camera.lookAt(0, 0, 0);
    
    // Create renderer
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(
        document.getElementById('visualization').offsetWidth,
        document.getElementById('visualization').offsetHeight
    );
    renderer.setClearColor(0x000000);
    document.getElementById('visualization').appendChild(renderer.domElement);
    
    // Remove loading indicator
    const loadingElement = document.getElementById('loading');
    if (loadingElement) {
        loadingElement.remove();
    }
    
    // Add ambient light
    const ambientLight = new THREE.AmbientLight(0xFFFFFF);  // Brighter ambient light
    scene.add(ambientLight);
    
    
    // Add subtle blue hemisphere light for better atmosphere simulation
    const hemiLight = new THREE.HemisphereLight(0x3284ff, 0x111111, 1);
    scene.add(hemiLight);
    
    // Create Earth
    createEarth();
    
    // Add orbit controls with restrictions
    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.minDistance = 15000; // Prevent zooming too close
    controls.maxDistance = 50000; // Prevent zooming too far
    controls.enablePan = false;   // Disable panning
    controls.maxPolarAngle = Math.PI / 1.5; // Limit vertical rotation
    controls.minPolarAngle = Math.PI / 4;   // Limit vertical rotation
    
    // Add impact visualization features
    addEarthClickHandler();
    
    // Start animation
    animate();
    
    // Handle window resize
    window.addEventListener('resize', onWindowResize, false);
}

function createEarth() {
    // Load Earth textures
    const textureLoader = new THREE.TextureLoader();
    const earthTexture = textureLoader.load(currentTexture.map);
    const bumpMap = textureLoader.load(currentTexture.bump);
    
    // Enhance texture quality
    earthTexture.anisotropy = renderer.capabilities.getMaxAnisotropy();
    earthTexture.encoding = THREE.sRGBEncoding;
    
    // Create Earth geometry with optimal segments for default texture
    const earthGeometry = new THREE.SphereGeometry(EARTH_RADIUS, 64, 64);
    const earthMaterial = new THREE.MeshPhongMaterial({
        map: earthTexture,
        bumpMap: bumpMap,
        bumpScale: 500,    // Reduced for better balance with default texture
        specular: new THREE.Color(0xFFFFFF),  // Darker specular for better contrast
        shininess: 5,      // Lower shininess for more matte appearance
        specularMap: bumpMap
    });
    
    // Enhance texture contrast
    earthTexture.encoding = THREE.sRGBEncoding;
    earthTexture.anisotropy = renderer.capabilities.getMaxAnisotropy();
    earthTexture.minFilter = THREE.LinearFilter;
    earthTexture.magFilter = THREE.LinearFilter;
    
    earth = new THREE.Mesh(earthGeometry, earthMaterial);
    scene.add(earth);
    
    // Add atmosphere glow with improved appearance
    const atmosphereGeometry = new THREE.SphereGeometry(EARTH_RADIUS + 150, 128, 128);
    const atmosphereMaterial = new THREE.MeshPhongMaterial({
        color: 0x3284ff,  // More natural blue color
        transparent: true,
        opacity: 0.15,
        side: THREE.BackSide,
        blending: THREE.AdditiveBlending  // Add additive blending for better glow
    });
    const atmosphere = new THREE.Mesh(atmosphereGeometry, atmosphereMaterial);
    // scene.add(atmosphere);
    
    // Add a subtle cloud layer
    const cloudGeometry = new THREE.SphereGeometry(EARTH_RADIUS + 50, 128, 128);
    const cloudMaterial = new THREE.MeshPhongMaterial({
        color: 0xffffff,
        transparent: true,
        opacity: 0.1,
        blending: THREE.AdditiveBlending
    });
    const clouds = new THREE.Mesh(cloudGeometry, cloudMaterial);
    scene.add(clouds);
}

function onWindowResize() {
    camera.aspect = document.getElementById('visualization').offsetWidth / document.getElementById('visualization').offsetHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(
        document.getElementById('visualization').offsetWidth,
        document.getElementById('visualization').offsetHeight
    );
}

function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
}

// Initialize when document is loaded
document.addEventListener('DOMContentLoaded', init);