# Velora Studio | AI Video Platform

Velora Studio is a state-of-the-art cinematic AI video generation platform. It enables users to create high-quality, photorealistic AI avatars and cinematic videos using advanced generative models and professional 3D pipelines.

## 🚀 Experience the Future of Video

This repository contains the core logic and interface for the Velora Studio platform, including:

- **Frontend**: A modern Next.js 15+ dashboard with professional avatar builders and intuitive video controls.
- **Backend**: A robust FastAPI service coordinating complex generation workflows across vast.ai and Modal.com.
- **3D Pipeline**: Integration with Blender and DAZ Studio assets for high-fidelity avatar morphs and animations.
- **GenAI Workflows**: Custom pipelines for LTX Video, Wan 2.2, and HunyuanVideo models.

## 🛠️ Technology Stack

- **Frontend**: Next.js (TypeScript), Tailwind CSS, Framer Motion, Three.js.
- **Backend**: Python (FastAPI), SQLAlchemy, Pydantic, Celery.
- **Infrastructure**: Docker, Modal (Serverless GPU), vast.ai (GPU Orchestration).
- **Core Models**: LTX-2, Wan 2.2, HunyuanVideo, FLUX.

## 📦 Getting Started

To run the project locally for development:

### 🔙 Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

### 🎨 Frontend
```bash
cd frontend
npm install
npm run dev -- -p 3015
```

## 📜 License
Private Repository. All rights reserved.
