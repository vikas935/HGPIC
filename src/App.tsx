import React, { useState } from 'react';
import { Send, MessageCircle, Dna, Box } from 'lucide-react';

interface Message {
  id: number;
  text: string;
  isUser: boolean;
  timestamp: Date;
}

function App() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      text: "Hello! I'm your AI assistant specialized in 3D models and gesture control systems. I'm connected to a real AI server and can answer any question you have!",
      isUser: false,
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleNavigation = (url: string) => {
    window.open(url, '_blank');
  };

  const sendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage: Message = {
      id: Date.now(),
      text: inputMessage,
      isUser: true,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      console.log('Sending request to chatbot server...');
      
      const response = await fetch('http://localhost:5001/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: inputMessage })
      });

      console.log('Response status:', response.status);
      
      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();
      console.log('Response data:', data);
      
      let responseText: string;
      
      if (data.response) {
        responseText = data.response;
      } else if (data.error) {
        responseText = `API Error: ${data.error}`;
      } else {
        responseText = 'Sorry, I received an unexpected response from the server.';
      }
      
      const aiMessage: Message = {
        id: Date.now() + 1,
        text: responseText,
        isUser: false,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: Message = {
        id: Date.now() + 1,
        text: `Connection error: ${error instanceof Error ? error.message : 'Unable to connect to AI server'}. Please ensure:\n\n1. Python chatbot server is running on port 5001\n2. Server is accessible at http://localhost:5001\n3. No firewall is blocking the connection`,
        isUser: false,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    }

    setIsLoading(false);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // Test server connection
  const testServerConnection = async () => {
    try {
      const response = await fetch('http://localhost:5001/');
      if (response.ok) {
        console.log('Server is accessible');
        return true;
      }
    } catch (error) {
      console.error('Server connection test failed:', error);
    }
    return false;
  };

  // Test connection on component mount
  React.useEffect(() => {
    testServerConnection();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">3D Control Dashboard</h1>
          <p className="text-gray-600">Navigate to applications and chat with real AI assistant</p>
        </div>

        {/* Top Half - Navigation Buttons */}
        <div className="mb-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {/* 3D Shapes Button */}
            <div className="bg-white rounded-xl shadow-lg p-8 text-center hover:shadow-xl transition-shadow duration-300">
              <div className="flex flex-col items-center">
                <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mb-6">
                  <Box className="w-10 h-10 text-blue-600" />
                </div>
                <h2 className="text-2xl font-semibold text-gray-800 mb-4">3D Shapes</h2>
                <p className="text-gray-600 mb-6">Explore interactive 3D models and shapes</p>
                <button
                  onClick={() => handleNavigation('/3d-shapes.html')}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-4 px-8 rounded-lg transition-colors duration-200 flex items-center justify-center group"
                >
                  <Box className="w-5 h-5 mr-3 group-hover:translate-x-1 transition-transform duration-200" />
                  Launch 3D Shapes
                </button>
              </div>
            </div>

            {/* DNA Visualization Button */}
            <div className="bg-white rounded-xl shadow-lg p-8 text-center hover:shadow-xl transition-shadow duration-300">
              <div className="flex flex-col items-center">
                <div className="w-20 h-20 bg-purple-100 rounded-full flex items-center justify-center mb-6">
                  <Dna className="w-10 h-10 text-purple-600" />
                </div>
                <h2 className="text-2xl font-semibold text-gray-800 mb-4">DNA Visualization</h2>
                <p className="text-gray-600 mb-6">Interactive DNA model with gesture control</p>
                <button
                  onClick={() => handleNavigation('/DNA2/index.html')}
                  className="w-full bg-purple-600 hover:bg-purple-700 text-white font-semibold py-4 px-8 rounded-lg transition-colors duration-200 flex items-center justify-center group"
                >
                  <Dna className="w-5 h-5 mr-3 group-hover:bounce transition-transform duration-200" />
                  Launch DNA Explorer
                </button>
              </div>
            </div>

            {/* Image to 3D Button */}
            <div className="bg-white rounded-xl shadow-lg p-8 text-center hover:shadow-xl transition-shadow duration-300">
              <div className="flex flex-col items-center">
                <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mb-6">
                  <div className="text-2xl">🖼️</div>
                </div>
                <h2 className="text-2xl font-semibold text-gray-800 mb-4">Image to 3D</h2>
                <p className="text-gray-600 mb-6">Upload image and control with gestures</p>
                <button
                  onClick={() => handleNavigation('/image-to-3d.html')}
                  className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-4 px-8 rounded-lg transition-colors duration-200 flex items-center justify-center group"
                >
                  <div className="w-5 h-5 mr-3 group-hover:scale-110 transition-transform duration-200">🖼️</div>
                  Launch Image to 3D
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Half - AI Chat Section */}
        <div className="max-w-6xl mx-auto">
          <div className="bg-white rounded-xl shadow-lg">
            {/* Chat Header */}
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center">
                <MessageCircle className="w-6 h-6 text-purple-600 mr-3" />
                <h2 className="text-2xl font-semibold text-gray-800">Real AI Assistant</h2>
              </div>
              <p className="text-sm text-gray-600 mt-1">Connected to AI server - Answers any question using real AI</p>
            </div>

            {/* Chat Messages */}
            <div className="h-96 overflow-y-auto p-6 space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                      message.isUser
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    <p className="text-sm whitespace-pre-wrap">{message.text}</p>
                    <p className={`text-xs mt-1 ${
                      message.isUser ? 'text-blue-200' : 'text-gray-500'
                    }`}>
                      {message.timestamp.toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              ))}
              
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 px-4 py-2 rounded-lg">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Chat Input */}
            <div className="p-6 border-t border-gray-200">
              <div className="flex space-x-3">
                <input
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask me anything - Connected to real AI server..."
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  disabled={isLoading}
                />
                <button
                  onClick={sendMessage}
                  disabled={isLoading || !inputMessage.trim()}
                  className="bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg transition-colors duration-200 flex items-center"
                >
                  <Send className="w-4 h-4" />
                </button>
              </div>
              
              {/* Connection Status */}
              <div className="mt-3 flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className={`w-2 h-2 rounded-full ${isLoading ? 'bg-yellow-500 animate-pulse' : 'bg-green-500'}`}></div>
                  <span className="text-xs text-gray-500">
                    {isLoading ? 'Connecting to AI...' : 'Connected to AI server'}
                  </span>
                </div>g
                <button
                  onClick={testServerConnection}
                  className="text-xs text-purple-600 hover:text-purple-800"
                >
                  Test Connection
                </button>
              </div>

              {/* Example Questions */}
              <div className="mt-4">
                <p className="text-xs text-gray-500 mb-2">Try asking anything:</p>
                <div className="flex flex-wrap gap-2">
                  {[
                    "What is artificial intelligence?",
                    "Explain quantum computing",
                    "How does GPS work?",
                    "Tell me about climate change",
                    "What are black holes?",
                    "How do airplanes fly?"
                  ].map((example, index) => (
                    <button
                      key={index}
                      onClick={() => setInputMessage(example)}
                      className="text-xs bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-1 rounded-full transition-colors duration-200"
                    >
                      {example}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;