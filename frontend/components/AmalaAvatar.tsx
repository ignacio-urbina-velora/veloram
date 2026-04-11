'use client';

import { useEffect, useRef } from 'react';
import { useGLTF } from '@react-three/drei';
import * as THREE from 'three';

interface AmalaAvatarProps {
  morphs: Record<string, number>;
  skinColor: string;
  eyeColor?: string;
  hairStyle: string;
  hairColor: string;
  onDebugUpdate: (stats: any) => void;
}

export default function AmalaAvatar({
  morphs,
  skinColor,
  onDebugUpdate,
}: AmalaAvatarProps) {
  const { scene } = useGLTF('/model/amala.glb');
  const groupRef = useRef<THREE.Group>(null);

  useEffect(() => {
    if (!scene) return;
    console.log('[AmalaAvatar] Modelo cargado correctamente');

    scene.traverse((child) => {
      if ((child as THREE.Mesh).isMesh) {
        const mesh = child as THREE.Mesh;
        // Material simple para diagnóstico
        mesh.material = new THREE.MeshStandardMaterial({
          color: new THREE.Color(skinColor),
          roughness: 0.6,
          metalness: 0.0,
        });
        mesh.castShadow = true;
        mesh.receiveShadow = true;
      }
    });

    onDebugUpdate({ loaded: true });
  }, [scene, skinColor, onDebugUpdate]);

  // Aplicar morphs si existen
  useEffect(() => {
    if (!scene) return;
    scene.traverse((child) => {
      const mesh = child as THREE.Mesh;
      if (mesh.isMesh && mesh.morphTargetDictionary && mesh.morphTargetInfluences) {
        Object.entries(morphs).forEach(([key, val]) => {
          const idx = mesh.morphTargetDictionary![key];
          if (idx !== undefined) {
            mesh.morphTargetInfluences![idx] = val;
          }
        });
      }
    });
  }, [scene, morphs]);

  if (!scene) return null;

  return (
    <group ref={groupRef} position={[0, -0.85, 0]}>
      <primitive object={scene} />
    </group>
  );
}

// Pre-cargar el modelo
useGLTF.preload('/model/amala.glb');
