from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app)

# Perplexity API Configuration
import os
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"

# Use sonar-pro model
MODEL = "sonar-pro"


print(f"🤖 Using model: {MODEL}")

@app.route('/')
def home():
    return jsonify({"status": "Server is running", "message": "Use /chat endpoint for AI"})

@app.route('/test-api', methods=['GET'])
def test_api():
    """Test the sonar-pro model"""
    try:
        headers = {
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": MODEL,
            "messages": [
                {"role": "user", "content": "What is 2+2? Answer with just the number."}
            ],
            "max_tokens": 10,
            "temperature": 0.1
        }
        
        print(f"🧪 Testing model: {MODEL}")
        response = requests.post(PERPLEXITY_API_URL, headers=headers, json=payload, timeout=30)
        
        result = {
            "model": MODEL,
            "status_code": response.status_code,
            "success": response.status_code == 200
        }
        
        if response.status_code == 200:
            ai_response = response.json()
            result["ai_response"] = ai_response
            result["answer"] = ai_response.get('choices', [{}])[0].get('message', {}).get('content', 'No content')
            print("✅ API test successful")
        else:
            result["error"] = response.text
            print(f"❌ API test failed: {response.status_code}")
            
        return jsonify(result)
        
    except Exception as e:
        print(f"💥 API test error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '')
        
        print(f"📨 Received: {user_message}")
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Prepare API request with sonar-pro
        headers = {
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": MODEL,
            "messages": [
                {
                    "role": "system", 
                    "content": """You are a helpful AI assistant specialized in 3D models and gesture control systems. 
                    Provide detailed, accurate responses to any question while maintaining a professional tone.
                    If the question is about 3D modeling, gesture control, VR/AR, or related technologies, provide expert-level insights.
                    For other topics, provide comprehensive and helpful information."""
                },
                {
                    "role": "user", 
                    "content": user_message
                }
            ],
            "max_tokens": 1500,
            "temperature": 0.7,
            "top_p": 0.9
        }
        
        print(f"🔄 Sending to Perplexity API with model: {MODEL}")
        
        response = requests.post(PERPLEXITY_API_URL, headers=headers, json=payload, timeout=30)
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            ai_response = response.json()
            print("✅ API call successful")
            
            if 'choices' in ai_response and len(ai_response['choices']) > 0:
                response_text = ai_response['choices'][0]['message']['content']
                return jsonify({
                    'response': response_text,
                    'source': 'perplexity_ai',
                    'model': MODEL
                })
            else:
                return jsonify({
                    'error': 'Unexpected response format from AI service'
                }), 500
                
        else:
            error_info = {
                'status_code': response.status_code,
                'error': response.text
            }
            print(f"❌ API Error: {error_info}")
            
            # Provide helpful error messages
            if response.status_code == 400:
                return jsonify({
                    'error': 'Bad request - invalid parameters',
                    'details': 'The request format might be incorrect'
                }), 500
            elif response.status_code == 401:
                return jsonify({
                    'error': 'Invalid API Key',
                    'details': 'Please check your Perplexity API key'
                }), 500
            elif response.status_code == 429:
                return jsonify({
                    'error': 'Rate Limit Exceeded',
                    'details': 'Too many requests. Please wait a moment.'
                }), 500
            else:
                return jsonify({
                    'error': f'API error {response.status_code}',
                    'details': response.text
                }), 500
    
    except requests.exceptions.Timeout:
        print("⏰ API request timeout")
        return jsonify({'error': 'API request timeout - server took too long to respond'}), 500
    except requests.exceptions.ConnectionError:
        print("🌐 Network connection error")
        return jsonify({'error': 'Network connection failed - check your internet'}), 500
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    print("🚀 Starting AI Server with sonar-pro...")
    print("📡 http://localhost:5001")
    print("🤖 Model: sonar-pro")
    print("🎯 Will answer ANY question with real AI")
    print("=" * 50)
    app.run(debug=True, port=5001, host='0.0.0.0')