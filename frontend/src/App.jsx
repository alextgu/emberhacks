// src/App.jsx
import React, { useEffect, useState } from 'react';
import { useWakeWord } from './hooks/useWakeWord';

function App() {
  const [detectedCount, setDetectedCount] = useState(0);
  const [lastDetected, setLastDetected] = useState(null);

  // Request microphone permission
  useEffect(() => {
    navigator.mediaDevices.getUserMedia({ audio: true })
      .then(() => console.log('✅ Microphone ready'))
      .catch((err) => console.error('❌ Mic denied:', err));
  }, []);

  // Wake word detection handler
  const handleWakeWord = () => {
    console.log('🎤 Hey Zed detected!');
    setDetectedCount(prev => prev + 1);
    setLastDetected(new Date().toLocaleTimeString());
    
    // Visual/audio feedback
    alert('Hey Zed detected! 🎉');
  };

  // Initialize wake word
  useWakeWord(
    process.env.REACT_APP_PORCUPINE_KEY,
    handleWakeWord
  );

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-2xl mx-auto bg-white rounded-lg shadow p-6">
        <h1 className="text-3xl font-bold mb-4">🎓 Zed Wake Word Test</h1>
        
        <div className="space-y-4">
          <div className="bg-blue-50 p-4 rounded">
            <p className="text-lg">🎤 Say: <strong>"Hey Zed"</strong></p>
            <p className="text-sm text-gray-600 mt-2">
              Speak clearly and wait for the alert
            </p>
          </div>

          <div className="bg-green-50 p-4 rounded">
            <p className="text-sm text-gray-600">Detections:</p>
            <p className="text-2xl font-bold">{detectedCount}</p>
            {lastDetected && (
              <p className="text-xs text-gray-500">Last: {lastDetected}</p>
            )}
          </div>

          <div className="text-xs text-gray-400">
            <p>✅ Check browser console for logs</p>
            <p>✅ Make sure microphone permission is granted</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;