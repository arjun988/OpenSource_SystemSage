import React, { useState, useRef, useEffect } from 'react';
import { FileText, Folder, Clock, Save, Terminal, MessageCircle, Mic, MicOff } from 'lucide-react';

const ChatWindow = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [showHistory, setShowHistory] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [mode, setMode] = useState('chat'); // 'chat' or 'command'
  const [isRecording, setIsRecording] = useState(false);
  const [recordingText, setRecordingText] = useState('');
  const messagesEndRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
    loadChatHistory();
  }, [messages]);

  const loadChatHistory = async () => {
    try {
      const response = await fetch('http://localhost:5000/chat_history');
      const history = await response.json();
      setChatHistory(history);
    } catch (error) {
      console.error('Error loading chat history:', error);
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        await transcribeAudio(audioBlob);
        
        // Stop all tracks to release the microphone
        stream.getTracks().forEach(track => track.stop());
      };

      // Setup for continuous transcription
      const transcriptionInterval = setInterval(async () => {
        if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
          mediaRecorderRef.current.requestData();
          const currentAudioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
          if (currentAudioBlob.size > 0) {
            await transcribeAudio(currentAudioBlob, true);
          }
        } else {
          clearInterval(transcriptionInterval);
        }
      }, 3000);  // Try to transcribe every 3 seconds

      mediaRecorderRef.current.start();
      setIsRecording(true);
      setRecordingText('Listening...');
    } catch (error) {
      console.error('Error starting recording:', error);
      setRecordingText('Error: ' + error.message);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      
      // Transfer the recording text to the input field
      if (recordingText && recordingText !== 'Listening...') {
        setInput(recordingText);
      }
      setRecordingText('');
    }
  };

  const transcribeAudio = async (audioBlob, isInterim = false) => {
    try {
      const formData = new FormData();
      formData.append('audio', audioBlob);

      const response = await fetch('http://localhost:5000/transcribe', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      
      if (data.transcription) {
        if (isInterim) {
          // For interim results, just update the recording text
          setRecordingText(data.transcription);
        } else {
          // For final results, set the input field
          setInput(data.transcription);
          setRecordingText('');
        }
      } else if (data.error) {
        setRecordingText(isInterim ? 'Listening...' : 'Error: ' + data.error);
      }
    } catch (error) {
      console.error('Error transcribing audio:', error);
      setRecordingText('Error transcribing audio');
    }
  };

  const renderStructure = (structure) => {
    return (
      <div className="ml-4 mt-2">
        {structure.map((item, index) => (
          <div key={index} className="flex items-center gap-2 text-gray-700">
            {item.type === 'folder' ? (
              <Folder className="w-4 h-4" />
            ) : (
              <FileText className="w-4 h-4" />
            )}
            {item.name}
          </div>
        ))}
      </div>
    );
  };

  const renderHistory = (history) => {
    return (
      <div className="ml-4 mt-2 bg-gray-50 p-3 rounded-lg">
        {history.map((item, index) => (
          <div key={index} className="mb-2 text-sm">
            <span className="text-gray-500">{new Date(item.timestamp).toLocaleString()}</span>
            <br />
            <strong>{item.sender}:</strong> {item.message}
          </div>
        ))}
      </div>
    );
  };

  const renderMessage = (msg, index) => {
    const isUserMessage = msg.sender === 'User';
    const messageClass = isUserMessage 
      ? 'ml-auto bg-blue-500 text-white' 
      : 'bg-gray-200 text-gray-800';

    return (
      <div 
        key={index} 
        className={`p-3 rounded-lg mb-2 max-w-[80%] ${messageClass}`}
      >
        <div className="flex items-center gap-2 font-semibold mb-1">
          {!isUserMessage && mode === 'command' && (
            <Terminal className="w-4 h-4" />
          )}
          {!isUserMessage && mode === 'chat' && (
            <MessageCircle className="w-4 h-4" />
          )}
          {msg.sender}
        </div>
        <div className="whitespace-pre-wrap">{msg.text}</div>
        {msg.structure && renderStructure(msg.structure)}
        {msg.history && renderHistory(msg.history)}
      </div>
    );
  };

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = { sender: 'User', text: input };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:5000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input }),
      });
      const data = await response.json();
      
      // Determine if the response is from a command or chat
      const isCommand = data.reply && (
        typeof data.reply === 'string' && (
          data.reply.includes('Created') ||
          data.reply.includes('Deleted') ||
          data.reply.includes('Volume') ||
          data.reply.includes('Brightness') ||
          data.reply.includes('Opened') ||
          data.reply.includes('Backed up')
        )
      );
      
      setMode(isCommand ? 'command' : 'chat');
      
      setMessages(prev => [...prev, { 
        sender: 'Bot', 
        text: data.reply,
        structure: data.structure,
        history: data.history 
      }]);
    } catch (error) {
      setMessages(prev => [...prev, { 
        sender: 'Bot', 
        text: `Error: ${error.message}` 
      }]);
    }
    
    setIsLoading(false);
    setInput('');
  };

  const getPlaceholderText = () => {
    if (isLoading) return "Processing...";
    if (isRecording) return "Listening...";
    return mode === 'command' 
      ? "Enter a command (e.g., 'increase volume', 'show files in downloads')" 
      : "Ask me anything...";
  };

  return (
    <div className="container mx-auto p-4 max-w-4xl">
      <div className="bg-white rounded-lg shadow-lg">
        <div className="flex items-center justify-between p-4 border-b">
          <div className="flex items-center gap-3">
            <h2 className="text-xl font-semibold">Assistant</h2>
            <div className="flex gap-2 text-sm">
              <button
                onClick={() => setMode('chat')}
                className={`px-3 py-1 rounded-full ${
                  mode === 'chat' 
                    ? 'bg-blue-100 text-blue-600' 
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                <div className="flex items-center gap-1">
                  <MessageCircle className="w-4 h-4" />
                  Chat
                </div>
              </button>
              <button
                onClick={() => setMode('command')}
                className={`px-3 py-1 rounded-full ${
                  mode === 'command' 
                    ? 'bg-blue-100 text-blue-600' 
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                <div className="flex items-center gap-1">
                  <Terminal className="w-4 h-4" />
                  Commands
                </div>
              </button>
            </div>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setShowHistory(!showHistory)}
              className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg"
              title="Show History"
            >
              <Clock className="w-5 h-5" />
            </button>
            <button
              onClick={loadChatHistory}
              className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg"
              title="Refresh"
            >
              <Save className="w-5 h-5" />
            </button>
          </div>
        </div>

        <div className="flex">
          <div className={`h-[70vh] overflow-y-auto p-4 ${showHistory ? 'w-2/3' : 'w-full'}`}>
            {messages.map((msg, index) => renderMessage(msg, index))}
            <div ref={messagesEndRef} />
          </div>

          {showHistory && (
            <div className="w-1/3 h-[70vh] overflow-y-auto p-4 border-l">
              <h3 className="font-semibold mb-3">Chat History</h3>
              {chatHistory.map((item, index) => (
                <div key={index} className="mb-3 text-sm">
                  <div className="text-gray-500 text-xs">
                    {new Date(item.timestamp).toLocaleString()}
                  </div>
                  <div>
                    <strong>{item.sender}:</strong> {item.message}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
        
        <div className="p-4 border-t">
          <div className="flex flex-col gap-2">
            {isRecording && (
              <div className="bg-red-50 text-red-600 p-2 rounded-lg text-sm">
                {recordingText || "Listening..."}
              </div>
            )}
            <div className="flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                placeholder={getPlaceholderText()}
                className="flex-1 p-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={isLoading}
              />
              <button
                onClick={isRecording ? stopRecording : startRecording}
                className={`p-2 rounded-lg transition-colors ${
                  isRecording 
                    ? 'bg-red-500 text-white hover:bg-red-600' 
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
                title={isRecording ? "Stop Recording" : "Start Recording"}
              >
                {isRecording ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
              </button>
              <button
                onClick={handleSend}
                className={`px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors ${
                  isLoading ? 'opacity-50 cursor-not-allowed' : ''
                }`}
                disabled={isLoading}
              >
                {isLoading ? 'Processing...' : 'Send'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatWindow;