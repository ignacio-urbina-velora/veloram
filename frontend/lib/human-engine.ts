import * as THREE from 'three';

export interface TargetMetadata {
  name: string;
  path: string;
  group: string;
}

export class HumanEngine {
  public geometry: THREE.BufferGeometry | null = null;
  public targets: Record<string, number> = {}; 
  private sparseTargets: Map<string, { indices: Uint32Array, values: Int16Array }> = new Map();
  private baseVertices: Float32Array | null = null;
  private nbVertices: number = 0;

  constructor() {}

  async initialize(baseMeshJson: any, targetListJson: any, targetsBin: ArrayBuffer) {
    console.log('Initializing HumanEngine: Optimized Mesh processing started...');
    
    // 1. Parse Base Mesh
    this.nbVertices = baseMeshJson.vertices.length / 3;
    this.baseVertices = new Float32Array(baseMeshJson.vertices);
    
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.BufferAttribute(this.baseVertices.slice(), 3));
    
    if (baseMeshJson.uvs && baseMeshJson.uvs[0]) {
      geometry.setAttribute('uv', new THREE.BufferAttribute(new Float32Array(baseMeshJson.uvs[0]), 2));
    }

    // Parse faces and filter proxies
    const indices: number[] = [];
    const faces = baseMeshJson.faces;
    let offset = 0;
    while (offset < faces.length) {
      const type = faces[offset++];
      const isQuad = type & 1;
      const hasMaterial = type & 2;
      const hasFaceUv = type & 4;
      const hasFaceVertexUv = type & 8;
      const hasFaceNormal = type & 16;
      const hasFaceVertexNormal = type & 32;
      const hasFaceColor = type & 64;
      const hasFaceVertexColor = type & 128;

      const vIndices: number[] = [];
      if (isQuad) vIndices.push(faces[offset++], faces[offset++], faces[offset++], faces[offset++]);
      else vIndices.push(faces[offset++], faces[offset++], faces[offset++]);

      let matIndex = 0;
      if (hasMaterial) matIndex = faces[offset++];
      
      if (matIndex === 0) { // Only body
        if (isQuad) {
          indices.push(vIndices[0], vIndices[1], vIndices[2]);
          indices.push(vIndices[0], vIndices[2], vIndices[3]);
        } else {
          indices.push(vIndices[0], vIndices[1], vIndices[2]);
        }
      }

      if (hasFaceUv) offset++;
      if (hasFaceVertexUv) offset += (isQuad ? 4 : 3);
      if (hasFaceNormal) offset++;
      if (hasFaceVertexNormal) offset += (isQuad ? 4 : 3);
      if (hasFaceColor) offset++;
      if (hasFaceVertexColor) offset += (isQuad ? 4 : 3);
    }
    
    geometry.setIndex(indices);
    geometry.computeVertexNormals();
    geometry.computeBoundingBox();
    geometry.computeBoundingSphere();
    this.geometry = geometry;

    // 2. Load and Sparse-ify Target Data
    const targetData = new Int16Array(targetsBin);
    const targetPaths = Object.keys(targetListJson.targets).sort();
    const m = this.nbVertices * 3;

    const importantPrefixes = [
      'data/targets/macrodetails/',
      'data/targets/head/',
      'data/targets/eyes/',
      'data/targets/nose/',
      'data/targets/mouth/',
      'data/targets/torso/',
      'data/targets/stomach/',
      'data/targets/hip/',
      'data/targets/buttocks/',
      'data/targets/breast/',
      'data/targets/chin/',
      'data/targets/cheek/'
    ];

    console.log(`Sparse-ifying relevant targets...`);
    
    for (let j = 0; j < targetPaths.length; j++) {
      const name = targetPaths[j];
      
      const isImportant = importantPrefixes.some(p => name.startsWith(p));
      if (!isImportant) continue;

      const start = j * m;
      
      // Count non-zeros
      let count = 0;
      for (let i = 0; i < m; i++) {
        if (targetData[start + i] !== 0) count++;
      }

      if (count > 0) {
        const indices = new Uint32Array(count);
        const values = new Int16Array(count);
        let ptr = 0;
        for (let i = 0; i < m; i++) {
          const val = targetData[start + i];
          if (val !== 0) {
            indices[ptr] = i;
            values[ptr] = val;
            ptr++;
          }
        }
        this.sparseTargets.set(name, { indices, values });
      }

      // Yield every 50 targets to avoid freezing
      if (j % 50 === 0) {
        await new Promise(resolve => setTimeout(resolve, 0));
      }
    }
    
    console.log(`Initialization complete. Kept ${this.sparseTargets.size} active targets.`);
  }

  applyInfluences(influences: Record<string, number>) {
    if (!this.geometry || !this.baseVertices) return;

    const positions = (this.geometry.attributes.position as THREE.BufferAttribute).array as Float32Array;
    positions.set(this.baseVertices);

    for (const [name, influence] of Object.entries(influences)) {
      if (Math.abs(influence) > 0.001) {
        const sparse = this.sparseTargets.get(name);
        if (sparse) {
          const { indices, values } = sparse;
          const factor = influence * 0.001;
          for (let k = 0; k < indices.length; k++) {
            positions[indices[k]] += values[k] * factor;
          }
        }
      }
    }

    this.geometry.attributes.position.needsUpdate = true;
    this.geometry.computeVertexNormals();
    this.geometry.computeBoundingBox();
    this.geometry.computeBoundingSphere();
  }
}
