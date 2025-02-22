// Add these script imports to your HTML head section

// Initialize scene, camera, and renderer
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(
  75,
  window.innerWidth / window.innerHeight,
  0.1,
  1000
);
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(window.devicePixelRatio);
document.getElementById("three-container").appendChild(renderer.domElement);

// Add lights
const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
scene.add(ambientLight);

const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
directionalLight.position.set(5, 5, 5);
scene.add(directionalLight);

const pointLight = new THREE.PointLight(0xacc2ef, 1);
pointLight.position.set(2, 3, 4);
scene.add(pointLight);

// Add OrbitControls
const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.05;
controls.screenSpacePanning = false;
controls.minDistance = 3;
controls.maxDistance = 10;
controls.maxPolarAngle = Math.PI / 2;

// Camera position
camera.position.set(0, 2, 5);

// Create particles
const particlesGeometry = new THREE.BufferGeometry();
const particlesCount = 2000;
const posArray = new Float32Array(particlesCount * 3);
const colorsArray = new Float32Array(particlesCount * 3);

for (let i = 0; i < particlesCount * 3; i += 3) {
  // Position
  posArray[i] = (Math.random() - 0.5) * 10;
  posArray[i + 1] = (Math.random() - 0.5) * 10;
  posArray[i + 2] = (Math.random() - 0.5) * 10;

  // Colors
  colorsArray[i] = 0.6 + Math.random() * 0.4; // R
  colorsArray[i + 1] = 0.7 + Math.random() * 0.3; // G
  colorsArray[i + 2] = 1; // B
}

particlesGeometry.setAttribute(
  "position",
  new THREE.BufferAttribute(posArray, 3)
);
particlesGeometry.setAttribute(
  "color",
  new THREE.BufferAttribute(colorsArray, 3)
);

const particlesMaterial = new THREE.PointsMaterial({
  size: 0.02,
  vertexColors: true,
  transparent: true,
  opacity: 0.8,
});

const particlesMesh = new THREE.Points(particlesGeometry, particlesMaterial);
scene.add(particlesMesh);

// Load Robot Model
const loader = new THREE.GLTFLoader();
let robot;

loader.load(
  "static/base_basic_shaded.glb", // Replace with your robot model path
  function (gltf) {
    robot = gltf.scene;
    robot.scale.set(2, 2, 2); // Adjust scale as needed
    robot.position.set(0, -1, 0); // Adjust position as needed
    scene.add(robot);

    // Auto-rotate the robot
    robot.rotation.y = Math.PI / 4;
  },
  function (xhr) {
    console.log((xhr.loaded / xhr.total) * 100 + "% loaded");
  },
  function (error) {
    console.error("An error occurred loading the model:", error);
  }
);

// Animation loop
let time = 0;
function animate() {
  requestAnimationFrame(animate);
  time += 0.001;

  // Animate particles
  particlesMesh.rotation.y += 0.0005;
  particlesMesh.rotation.x += 0.0002;

  // Make particles move in a wave pattern
  const positions = particlesGeometry.attributes.position.array;
  for (let i = 0; i < positions.length; i += 3) {
    positions[i + 1] += Math.sin(time + positions[i] * 0.5) * 0.002;
  }
  particlesGeometry.attributes.position.needsUpdate = true;

  // Rotate robot if loaded
  if (robot) {
    robot.rotation.y += 0.005;
  }

  // Update controls
  controls.update();

  renderer.render(scene, camera);
}

// Handle window resize
window.addEventListener("resize", onWindowResize, false);

function onWindowResize() {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
}

// Add mouse interaction with particles
let mouseX = 0;
let mouseY = 0;

document.addEventListener("mousemove", (event) => {
  mouseX = (event.clientX - window.innerWidth / 2) * 0.0002;
  mouseY = (event.clientY - window.innerHeight / 2) * 0.0002;

  if (robot) {
    robot.rotation.y += mouseX * 0.5;
    robot.rotation.x += mouseY * 0.5;
  }
});

// Start animation
animate();

// Optional: Add GUI controls for particle system
// Uncomment if you want to add adjustable controls
/*
const gui = new dat.GUI();
const parameters = {
    particleCount: particlesCount,
    particleSize: 0.02,
    particleOpacity: 0.8,
    rotationSpeed: 0.005
};

gui.add(parameters, 'particleSize', 0.01, 0.1).onChange((value) => {
    particlesMaterial.size = value;
});

gui.add(parameters, 'particleOpacity', 0, 1).onChange((value) => {
    particlesMaterial.opacity = value;
});

gui.add(parameters, 'rotationSpeed', 0.001, 0.01).onChange((value) => {
    rotationSpeed = value;
});
*/
