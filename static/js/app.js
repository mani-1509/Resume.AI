// Three.js Animation
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(
  75,
  window.innerWidth / window.innerHeight,
  0.1,
  1000
);
const renderer = new THREE.WebGLRenderer({
  canvas: document.querySelector("#three-container"),
  alpha: true,
});

renderer.setSize(window.innerWidth, window.innerHeight);

// Create animated background particles
const particlesGeometry = new THREE.BufferGeometry();
const particlesCount = 5000;
const posArray = new Float32Array(particlesCount * 3);

for (let i = 0; i < particlesCount * 3; i++) {
  posArray[i] = (Math.random() - 0.5) * 5;
}

particlesGeometry.setAttribute(
  "position",
  new THREE.BufferAttribute(posArray, 3)
);

const particlesMaterial = new THREE.PointsMaterial({
  size: 0.005,
  color: "#acc2ef",
});

const particlesMesh = new THREE.Points(particlesGeometry, particlesMaterial);
scene.add(particlesMesh);

camera.position.z = 2;

function animate() {
  requestAnimationFrame(animate);
  particlesMesh.rotation.y += 0.001;
  renderer.render(scene, camera);
}

animate();

// Handle window resize
window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// GSAP Animations
gsap.from(".hero-text", {
  duration: 1,
  y: 100,
  opacity: 0,
  ease: "power4.out",
});

gsap.from(".feature-card", {
  duration: 0.8,
  y: 50,
  opacity: 0,
  stagger: 0.2,
  ease: "power3.out",
  delay: 0.5,
});
