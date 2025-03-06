from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import subprocess
import random
from dotenv import load_dotenv
import google.generativeai as ggi
import screen_brightness_control as sbc
import psutil
import re
import sqlite3
from datetime import datetime
import shutil
import speech_recognition as sr

app = Flask(__name__)
CORS(app)

# Load environment variables
load_dotenv()
ggi.configure(api_key=os.getenv("gemini_gpt_key"))
chat = ggi.GenerativeModel("gemini-2.0-flash").start_chat()

# Enhanced system prompt
SYSTEM_PROMPT = """
You are an advanced AI assistant with multiple capabilities:
1. Execute system commands
2. Manage files and system settings
3. Engage in natural conversations
4. Provide technical assistance

Your goal is to understand user intent and respond appropriately. 
When processing commands, return a JSON object with these possible structures:

- Volume: {"command": "volume", "params": ["increase"/"decrease"]}
- Brightness: {"command": "brightness", "params": ["increase"/"decrease"]}
- Version Check: {"command": "version", "params": ["framework_name"]}
- App Check: {"command": "app", "params": ["app_name"]}
- File Operations: {"command": "file", "params": ["action", "filepath"]}
- Folder Operations: {"command": "folder", "params": ["action", "path"]}
- Code Operations: {"command": "code", "params": ["action", "filepath"]}
- Open VSCode: {"command": "openvscode", "params": []}
- Open Application: {"command": "openapp", "params": ["app_name"]}
- Create Folder at Path: {"command": "createfolder", "params": ["folder_name", "path"]}
- Create File at Path: {"command": "createfile", "params": ["file_name", "path"]}

Conversation Guidelines:
- Be helpful and context-aware
- Provide clear and concise responses
- Adapt to user's communication style
"""

# Initialize database
def init_db():
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  sender TEXT NOT NULL,
                  message TEXT NOT NULL,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

# Existing command handler functions remain the same
def get_current_volume():
    """Fetches the current system volume (0-100%)."""
    try:
        output = subprocess.check_output(
            'powershell -c "$vol = (New-Object -ComObject WScript.Shell).SendKeys([char]174); '
            '$volume = (New-Object -ComObject SAPI.SpVoice).Volume; $volume"', 
            shell=True
        ).decode().strip()
        return float(output)
    except Exception:
        return None

def set_volume(volume):
    """Sets the system volume to a specified percentage (0-100%)."""
    os.system(f'powershell -c "(New-Object -ComObject WScript.Shell).SendKeys([char]174); '
              '(New-Object -ComObject SAPI.SpVoice).Volume = {volume}"')

def handle_volume(action):
    try:
        current_volume = get_current_volume()
        if current_volume is None:
            return "Error getting current volume."

        change = 10  # Increase/decrease by 10%
        new_volume = max(0, min(100, current_volume + change if action == 'increase' else current_volume - change))

        set_volume(new_volume)
        return f"Volume set to {new_volume}%"
    except Exception as e:
        return f"Error adjusting volume: {str(e)}"

def handle_brightness(action):
    try:
        current = sbc.get_brightness()[0]
        new_brightness = current + 10 if action == 'increase' else current - 10
        sbc.set_brightness(new_brightness)
        return f"Brightness {action}d to {new_brightness}%"
    except Exception as e:
        return f"Error adjusting brightness: {str(e)}"

def handle_version_check(framework):
    try:
        if framework.lower() == 'python':
            cmd = ['python', '--version']
        elif framework.lower() == 'pip':
            cmd = ['pip', '--version']
        elif framework.lower() == 'node':
            cmd = ['node', '--version']
        elif framework.lower() == 'npm':
            cmd = ['npm', '--version']
        else:
            return f"Version check not supported for {framework}"
        
        result = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        return f"{framework} version: {result.decode().strip()}"
    except Exception as e:
        return f"Could not get version for {framework}: {str(e)}"

def handle_app_check(app_name):
    try:
        installed = any(app_name.lower() in p.name().lower() for p in psutil.process_iter())
        return f"{app_name} is {'installed' if installed else 'not installed'}"
    except Exception as e:
        return f"Error checking app: {str(e)}"

def handle_file_operation(action, filepath):
    try:
        filepath = os.path.abspath(os.path.normpath(filepath))
        
        if action not in ['create', 'delete', 'read']:
            return f"Invalid file operation: {action}"
        
        directory = os.path.dirname(filepath)
        
        if action == 'create':
            if directory:
                os.makedirs(directory, exist_ok=True)
            with open(filepath, 'w') as f:
                f.write('')
            return f"Created file: {filepath}"
            
        elif action == 'delete':
            if not os.path.exists(filepath):
                return f"File not found: {filepath}"
            os.remove(filepath)
            return f"Deleted file: {filepath}"
            
        elif action == 'read':
            if not os.path.exists(filepath):
                return f"File not found: {filepath}"
            with open(filepath, 'r') as f:
                content = f.read()
            return f"Content of {filepath}:\n{content}"
            
    except PermissionError:
        return f"Permission denied: Cannot perform {action} operation on {filepath}"
    except Exception as e:
        return f"File operation error: {str(e)}"

def create_folder_in_vscode(folder_name, folder_path=None):
    try:
        if not folder_path:
            folder_path = os.getcwd()

        full_path = os.path.join(folder_path, folder_name)
        
        if not os.path.exists(full_path):
            os.makedirs(full_path)
            return f"Folder '{folder_name}' created successfully at '{folder_path}'."
        else:
            return f"Folder '{folder_name}' already exists at '{folder_path}'."
    except Exception as e:
        return f"Error creating folder: {str(e)}"

def handle_code_operation(action, filepath):
    try:
        with open(filepath, 'r') as f:
            code = f.read()
        response = chat.send_message(f"Validate this code and suggest improvements:\n{code}")
        return f"Code validation for {filepath}:\n{response.text}"
    except Exception as e:
        return f"Code operation error: {str(e)}"

# New function to open VSCode
def open_vscode():
    """Opens Visual Studio Code using direct methods for Windows."""
    try:
        # Method 1: Using PowerShell Start-Process
        try:
            subprocess.run(
                ["powershell", "-Command", "Start-Process code"],
                shell=True,
                check=True,
                capture_output=True
            )
            return "VS Code opened successfully using PowerShell."
        except subprocess.CalledProcessError:
            pass

        # Method 2: Try specific common installation paths
        common_paths = [
            r"C:\Program Files\Microsoft VS Code\Code.exe",
            r"C:\Program Files (x86)\Microsoft VS Code\Code.exe",
            r"C:\Users\arjun\AppData\Local\Programs\Microsoft VS Code\Code.exe",
            r"C:\Users\Administrator\AppData\Local\Programs\Microsoft VS Code\Code.exe"
        ]

        current_username = os.getenv("USERNAME") or "User"
        user_path = fr"C:\Users\{current_username}\AppData\Local\Programs\Microsoft VS Code\Code.exe"
        if user_path not in common_paths:
            common_paths.append(user_path)

        for path in common_paths:
            if os.path.exists(path):
                subprocess.Popen([path])
                return f"VS Code opened successfully from {path}"

        # Method 3: Try via Start Menu shortcut location
        start_menu_paths = [
            fr"C:\Users\{current_username}\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Visual Studio Code.lnk",
            r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Visual Studio Code.lnk"
        ]
        
        for path in start_menu_paths:
            if os.path.exists(path):
                subprocess.run(["cmd", "/c", "start", "", path], shell=True)
                return f"VS Code opened successfully via shortcut at {path}"

        # Method 4: Last resort - try direct command
        os.system("start code")
        return "Attempted to open VS Code using generic start command."
            
    except Exception as e:
        return f"Error opening Visual Studio Code: {str(e)}. Please check if it's installed."
# New function to open any desktop application
def open_application(app_name):
    """Opens any desktop application by name."""
    system = platform.system()
    try:
        if system == 'Windows':
            subprocess.Popen([app_name])
        elif system == 'Darwin':  # macOS
            subprocess.Popen(['open', '-a', app_name])
        elif system == 'Linux':
            subprocess.Popen([app_name])
        return f"{app_name} opened successfully."
    except Exception as e:
        return f"Error opening {app_name}: {e}"

# New function to create folder at specific path
def create_folder_at_path(folder_name, path):
    """Creates a folder at the specified path."""
    try:
        full_path = os.path.join(path, folder_name) if path else folder_name
        os.makedirs(full_path, exist_ok=True)
        return f"Folder '{folder_name}' created successfully at '{path}'."
    except Exception as e:
        return f"Error creating folder: {str(e)}"

# New function to create file at specific path
def create_file_at_path(file_name, path):
    """Creates an empty file at the specified path."""
    try:
        full_path = os.path.join(path, file_name) if path else file_name
        directory = os.path.dirname(full_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        with open(full_path, 'w') as f:
            pass  # Create empty file
        return f"File '{file_name}' created successfully at '{path}'."
    except Exception as e:
        return f"Error creating file: {str(e)}"

def handle_vscode():
    try:
        vscode_shortcut = r"C:\Users\arjun\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Visual Studio Code.lnk"

        if not os.path.exists(vscode_shortcut):
            return f"VS Code shortcut '{vscode_shortcut}' does not exist."

        subprocess.run(["cmd", "/c", "start", "", vscode_shortcut], shell=True)
        return "VS Code opened successfully."
    except Exception as e:
        return f"Error opening VS Code: {str(e)}"


def save_message(sender, message):
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute('INSERT INTO messages (sender, message) VALUES (?, ?)',
              (sender, message))
    conn.commit()
    conn.close()

# Enhanced conversation handling
def handle_conversation(message):
    try:
        greeting_keywords = ['hi', 'hello', 'hey', 'greetings', 'sup', 'howdy', 'hola']
        code_keywords = ['code', 'program', 'programming', 'python', 'development', 'developer', 'coding']
        help_keywords = ['help', 'assist', 'support', 'guidance']
        
        normalized_message = message.lower()
        
        if any(keyword in normalized_message for keyword in greeting_keywords):
            responses = [
                "Hello! I'm your AI assistant. How can I help you today?",
                "Hi there! What can I do for you?",
                "Greetings! I'm ready to assist you."
            ]
            return random.choice(responses)
        
        if any(keyword in normalized_message for keyword in help_keywords):
            return "I can help with system commands, file management, code queries, and more. What do you need?"
        
        if any(keyword in normalized_message for keyword in code_keywords):
            response = chat.send_message(f"Provide a professional response about: {message}")
            return response.text
        
        generic_response = chat.send_message(f"Respond helpfully to: {message}")
        return generic_response.text
    
    except Exception as e:
        return f"Error processing message: {str(e)}"

# Enhanced command routing
def route_command(command_data):
    try:
        command = command_data.get('command', '').lower()
        params = command_data.get('params', [])
        
        # Updated command handlers dictionary with new functions
        command_handlers = {
            'volume': lambda: handle_volume(params[0]),
            'brightness': lambda: handle_brightness(params[0]),
            'version': lambda: handle_version_check(params[0]),
            'app': lambda: handle_app_check(params[0]),
            'file': lambda: handle_file_operation(params[0], params[1]),
            'folder': lambda: create_folder_in_vscode(params[0], params[1] if len(params) > 1 else None),
            'code': lambda: handle_code_operation(params[0], params[1]),
            # 'vscode': lambda: handle_vscode(),
            'openvscode': lambda: open_vscode(),
            'openapp': lambda: open_application(params[0]),
            'createfolder': lambda: create_folder_at_path(params[0], params[1] if len(params) > 1 else None),
            'createfile': lambda: create_file_at_path(params[0], params[1] if len(params) > 1 else None)
        }
        
        handler = command_handlers.get(command)
        if not handler:
            return f"Command not recognized: {command}. Try a different command or ask for help."
            
        if not isinstance(params, list):
            return "Invalid params format: must be a list"
            
        return handler()
        
    except Exception as e:
        return f"Error processing command: {str(e)}"

# Speech-to-text functionality
recognizer = sr.Recognizer()

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    """Listen to speech and transcribe it in real-time"""
    with  sr.Microphone()  as source:
        print("Listening for live transcription...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
        except sr.WaitTimeoutError:
            print("No speech detected")
            return jsonify({"error": "No speech detected. Please try again."}), 400

    try:
        # Use Google's speech recognition
        recognized_text = recognizer.recognize_google(audio)
        print(f"Recognized: {recognized_text}")
        return jsonify({"transcription": recognized_text})
    except sr.UnknownValueError:
        print("Speech not understood")
        return jsonify({"error": "Speech not understood. Please try again."}), 400
    except sr.RequestError as e:
        print(f"API error: {e}")
        return jsonify({"error": f"Error: {e}"}), 500

@app.route('/chat', methods=['POST'])
def process_message():
    try:
        message = request.json.get('message')
        if not message:
            return jsonify({"error": "No message provided"}), 400
            
        save_message('User', message)
        
        try:
            response = chat.send_message(
                SYSTEM_PROMPT + f"\nUser request: {message}"
            )
            
            try:
                command_data = json.loads(response.text)
                
                if command_data.get('command'):
                    result = route_command(command_data)
                    save_message('Bot', str(result))
                    return jsonify({"reply": result})
            except json.JSONDecodeError:
                pass
        except Exception as e:
            pass
        
        conversation_response = handle_conversation(message)
        save_message('Bot', conversation_response)
        return jsonify({"reply": conversation_response})
            
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/chat_history', methods=['GET'])
def get_chat_history():
    limit = request.args.get('limit', 50)
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute('SELECT sender, message, timestamp FROM messages ORDER BY timestamp DESC LIMIT ?', (limit,))
    history = c.fetchall()
    conn.close()
    return jsonify([{"sender": h[0], "message": h[1], "timestamp": h[2]} for h in history])

# Add missing import for platform module
import platform

if __name__ == "__main__":
    app.run(debug=True)