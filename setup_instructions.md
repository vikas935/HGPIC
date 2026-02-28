# 3D Gesture Control Dashboard Setup

## Prerequisites
- Node.js (for the React dashboard)
- Python 3.8+ (for the AI chatbot)
- Gemini API key from Google AI Studio

## Setup Instructions

### 1. React Dashboard Setup
The dashboard is already configured and ready to run with Vite.

### 2. Python Chatbot Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Get Gemini API Key:**
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Copy the API key

3. **Configure API Key:**
   - Open `chatbot_server.py`
   - Replace `"your_gemini_api_key_here"` with your actual API key:
     ```python
     GEMINI_API_KEY = "your_actual_api_key_here"
     ```

4. **Run the chatbot server:**
   ```bash
   python chatbot_server.py
   ```
   The server will start at `http://localhost:5000`

## Usage

1. **Start the React dashboard:**
   ```bash
   npm run dev
   ```

2. **Start the Python chatbot server:**
   ```bash
   python chatbot_server.py
   ```

3. **Navigate through the dashboard:**
   - Click "Open Main Application" to go to index.html
   - Click "Launch AI Assistant" to open the chatbot at localhost:5000

## AI Chatbot Features

The chatbot specializes in:
- **3D Model Expertise**: Techniques, optimization, formats, rendering
- **Gesture Control Systems**: Recognition, tracking, processing
- **Industry Applications**: Healthcare, education, gaming, automotive, etc.

## Example Questions for the AI:

- "What are the best practices for optimizing 3D models for real-time rendering?"
- "How do gesture control systems work in VR applications?"
- "What are the applications of gesture-controlled 3D visualization in healthcare?"
- "Explain the latest hand tracking technologies"
- "How is gesture-controlled 3D modeling used in automotive design?"

## Troubleshooting

1. **API Key Error**: Make sure your Gemini API key is valid and correctly set
2. **Port Conflicts**: If port 5000 is busy, change it in `chatbot_server.py`
3. **CORS Issues**: The Flask server includes CORS headers for cross-origin requests