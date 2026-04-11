# Guía Maestra: Motor Hiperrealista v2.1 (Amala AI)

Esta guía documenta la arquitectura técnica y las mejores prácticas para generar avatares 2D con calidad fotográfica "8K Raw" utilizando el pipeline optimizado en Modal.

## 1. Arquitectura del Motor
El sistema no es un simple generador de imágenes, sino un pipeline de post-procesado quirúrgico dividido en 4 capas:

1.  **Capa Estructural (ControlNet Depth):**
    *   **Función:** Toma el maniquí 3D y crea un mapa de profundidad.
    *   **Importancia:** Garantiza que la cara de la IA tenga la misma geometría que el modelo 3D (nariz, mandíbula, pómulos). Sin esto, la IA "inventaría" una cara diferente cada vez.
2.  **Capa de Generación Base (FLUX.1-dev):**
    *   **Función:** Es el motor principal que interpreta el comando (prompt).
    *   **Ventaja:** Flux maneja las texturas de piel (poros, vello fino, humedad de los ojos) mucho mejor que Stable Diffusion.
3.  **Capa de Restauración Facial (CodeFormer/facexlib):**
    *   **Función:** Detecta el rostro y lo reconstruye digitalmente.
    *   **Efecto:** Le da esa nitidez "Ultra-HD" a los ojos y labios que es imposible obtener solo con generación base.
4.  **Capa de Ingeniería de Memoria (Sequential CPU Offload):**
    *   **Función:** Mueve el modelo entre RAM y VRAM.
    *   **Importancia:** Permite que un modelo de 30GB corra en una GPU de 24GB sin colapsar.

---

## 2. El Prompt Maestro (Hiperrealismo Extremo)
Para obtener los mejores resultados, el sistema inyecta este prompt técnico:

> **Positive Prompt:** _"ultra photorealistic close-up portrait, 8k raw photo, captured with Canon EOS R5, 85mm f/1.2 lens, sharp focus on eyes, micro-detail skin pores, natural skin texture, visible peach fuzz, cinematic lighting, dramatic studio shadows, realistic iris reflections, hyper-detailed hair strands, highly detailed professional photography."_

**Clave del éxito:** Al mencionar la cámara **Canon EOS R5**, la IA simula la profundidad de campo y la calidad del sensor de una cámara de 5.000 USD.

---

## 3. Mejores Prácticas para el Usuario
Para maximizar la calidad desde el editor 3D:
1.  **Iluminación:** Asegúrate de que el maniquí 3D tenga luz frontal. La IA usa las sombras del 3D para entender dónde poner los volúmenes del rostro real.
2.  **Pose:** Evita manos que tapen la cara. Aunque Flux es bueno con las manos, los ControlNets de profundidad pueden confundirse si hay demasiada oclusión.
3.  **Tiers de Calidad:**
    *   **Cinematic:** 40 pasos (Máxima calidad, tarda ~60s).
    *   **Professional:** 35 pasos (Equilibrio ideal, tarda ~45s).
    *   **Quick:** 25 pasos (Para pruebas rápidas, tarda ~20s).

---

## 4. Notas de Infraestructura
Todo el motor corre en **Modal** con hardware **NVIDIA A10G**. Hemos optimizado la carga de pesos desde volúmenes persistentes para minimizar el tiempo de "Cold Start".

> [!TIP]
> Si la imagen sale con la piel demasiado suave, añade al prompt: **"unfiltered skin, non-retouched, high frequency skin texture"**.

---
*Documento generado por Antigravity AI - 2026*
