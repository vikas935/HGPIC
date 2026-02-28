# 🧬 HGPIC – Hybrid Generative Processing & Interactive Creator

HGPIC is a full-stack AI-powered interactive platform that combines 3D visualization, image processing, chatbot intelligence, and scientific visualization (DNA modeling) into a unified system.

This project demonstrates integration of:

- 🧠 AI Chatbot backend
- 🖼️ Image-to-3D conversion
- 🧬 DNA structure visualization
- ⚛️ Modern React + Vite frontend
- 🐍 Python-based AI services

---

## 🚀 Features

- 🧬 Interactive DNA visualization module
- 🖼️ Image to 3D model rendering
- 🤖 AI chatbot server integration
- ⚛️ Modern frontend using React + Vite
- 🎨 TailwindCSS UI styling
- 🐍 Python backend for AI processing
- 📦 Full-stack architecture

---

## 🛠️ Tech Stack

### Frontend
- React (Vite)
- TypeScript
- Tailwind CSS
- HTML / CSS

### Backend
- Python
- Flask
- REST APIs

### AI / Processing
- Image processing modules
- External LLM API integration (via environment variables)

---

## 📂 Project Structure

```
HGPIC/
│
├── chatbot_server.py
├── image_processor.py
├── main.py
├── requirements.txt
│
├── src/                 # React frontend
├── DNA2/                # DNA visualization module
├── 3d-shapes.html       # 3D rendering page
├── image-to-3d.html
│
├── package.json
├── vite.config.ts
└── README.md
```

---

## ⚙️ Installation Guide

### 1️⃣ Clone Repository

```bash
git clone https://github.com/vikas935/HGPIC.git
cd HGPIC
```

---

### 2️⃣ Backend Setup (Python)

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file (not committed to GitHub):

```
PERPLEXITY_API_KEY=your_api_key_here
```

Run backend:

```bash
python chatbot_server.py
```

---

### 3️⃣ Frontend Setup (React)

```bash
npm install
npm run dev
```

---

## 🔐 Security

API keys are managed via environment variables and excluded from version control using `.gitignore`.

---

## 🎯 Use Cases

- AI-assisted scientific visualization
- Educational 3D DNA modeling
- Interactive AI chatbot systems
- Image-to-3D experimental conversion
- Hybrid AI full-stack applications

---

## 🚀 Future Improvements

- Full authentication system
- Database integration
- Advanced 3D rendering pipeline
- Deployment to cloud (Render / Vercel)
- Model optimization

---

## 👨‍💻 Author

**Vikas CR**  
AI & Machine Learning Enthusiast  
GitHub: https://github.com/vikas935

---

⭐ If you like this project, give it a star!