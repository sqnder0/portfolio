import * as THREE from "three";
import WebGL from "three/addons/capabilities/WebGL.js";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";

let hidden;
if (WebGL.isWebGLAvailable()) {
  const scene = new THREE.Scene();
  const loader = new GLTFLoader();
  const pc = document.getElementById("pc");
  let camera;
  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setClearColor(0xffffff, 0);
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.setSize(pc.offsetWidth, pc.offsetHeight);
  pc.appendChild(renderer.domElement);
  loader.load(
    "3d models/pc.glb",
    function (gltf) {
      camera = new THREE.PerspectiveCamera(
        20,
        pc.offsetWidth / pc.offsetHeight,
        0.01,
        1000
      );
      camera.position.set(-0.7, 0.133, 1);
      camera.rotation.y = -0.37;
      gltf.scene.scale.multiplyScalar(1.2 / 1);
      scene.add(gltf.scene);

      animate();
    },
    undefined,
    function (error) {
      console.error(error);
    }
  );
  function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
  }
  window.addEventListener("resize", () => {
    renderer.setSize(pc.offsetWidth, pc.offsetHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    if (camera.aspect) {
      camera.aspect = pc.offsetWidth / pc.offsetHeight;
      camera.updateProjectionMatrix();
    }
    if (window.innerWidth <= 860) {
      console.log(hidden);
      hidden = true;
    }
    if (window.innerWidth >= 860 && hidden == true) {
      window.location.reload();
    }
  });
} else {
  const warning = WebGL.getWebGLErrorMessage();
  document.getElementById("container").appendChild(warning);
}
