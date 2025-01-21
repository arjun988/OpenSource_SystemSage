from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import subprocess
from dotenv import load_dotenv
import google.generativeai as ggi
import screen_brightness_control as sbc
import psutil
import re
import sqlite3
from datetime import datetime
import shutil

app = Flask(__name__)
CORS(app)

# Load environment variables
load_dotenv()
ggi.configure(api_key=os.getenv("gemini_gpt_key"))
chat = ggi.GenerativeModel("gemini-pro").start_chat()

# System prompt for command interpretation
SYSTEM_PROMPT = """
You are a virtual assistant capable of controlling system settings and managing files and can also make causal conversations. When users make requests, return a JSON object with specific command structures:

1. For volume control: 
   {"command": "volume", "params": ["increase" or "decrease"]}

2. For brightness: 
   {"command": "brightness", "params": ["increase" or "decrease"]}

3. For version checks: 
   {"command": "version", "params": ["python" or other framework name]}

4. For application checks: 
   {"command": "app", "params": ["application_name"]}

5. For file operations: 
   {"command": "file", "params": ["create/delete/read", "filepath"]}

6. For folder operations: 
   {"command": "folder", "params": ["list", "folder_path"]}

7. For code operations: 
   {"command": "code", "params": ["validate", "filepath"]}

8. For VS Code: 
   {"command": "vscode", "params": ["filepath"]}

9. For path creation: 
   {"command": "create_path", "params": ["filepath"]}

10. For chat history: 
    {"command": "history", "params": []}

11. For backup operations: 
    {"command": "backup", "params": ["type", "source_path", "destination_path"]}

Always return a valid JSON object with these exact command structures.
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

# Command handler functions
def handle_volume(action):
    try:
        if action == 'increase':
            os.system("amixer -D pulse sset Master 5%+")
        else:
            os.system("amixer -D pulse sset Master 5%-")
        return f"Volume {action}d by 5%"
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
        # Use the current working directory if no folder_path is provided
        if not folder_path:
            folder_path = os.getcwd()

        # Handle spaces in the path by enclosing in quotes
        full_path = os.path.join(folder_path, folder_name)
        
        if not os.path.exists(full_path):
            os.makedirs(full_path)
            return f"Folder '{folder_name}' created successfully at '{folder_path}'."
        else:
            return f"Folder '{folder_name}' already exists at '{folder_path}'."
    except Exception as e:
        return f"An error occurred while creating the folder '{folder_name}' in '{folder_path}': {str(e)}"

def handle_code_operation(action, filepath):
    try:
        with open(filepath, 'r') as f:
            code = f.read()
        response = chat.send_message(f"Validate this code and suggest improvements:\n{code}")
        return f"Code validation for {filepath}:\n{response.text}"
    except Exception as e:
        return f"Code operation error: {str(e)}"

def handle_vscode(path):
    try:
        # Handle spaces in the path by enclosing it in quotes
        if os.path.exists(path):
            os.system(f'code "{path}"')  # Open VSCode at the specified path.
            return f"VSCode opened at path '{path}' successfully."
        else:
            return f"The specified path '{path}' does not exist."
    except Exception as e:
        return f"An error occurred while opening VSCode at path '{path}': {str(e)}"

def handle_create_path(filepath):
    try:
        filepath = os.path.normpath(filepath)
        
        directory = os.path.dirname(filepath) if os.path.dirname(filepath) else '.'
        if not os.access(directory, os.W_OK):
            return f"Permission denied: Cannot write to {directory}. Try running the application as administrator."
            
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        try:
            with open(filepath, 'w') as f:
                f.write('')
            return f"Created file at: {filepath}"
        except PermissionError:
            return f"Permission denied: Cannot create file at {filepath}. Try running as administrator."
    except Exception as e:
        return f"Error creating file: {str(e)}\nTry running the application as administrator."

def handle_history():
    try:
        conn = sqlite3.connect('chat_history.db')
        c = conn.cursor()
        c.execute('SELECT sender, message, timestamp FROM messages ORDER BY timestamp DESC LIMIT 50')
        history = c.fetchall()
        conn.close()
        return {"message": "Here's your chat history:", 
                "history": [{"sender": h[0], "message": h[1], "timestamp": h[2]} for h in history]}
    except Exception as e:
        return f"Error fetching history: {str(e)}"

def handle_search(term):
    try:
        conn = sqlite3.connect('chat_history.db')
        c = conn.cursor()
        c.execute('SELECT sender, message, timestamp FROM messages WHERE message LIKE ? ORDER BY timestamp DESC',
                 (f'%{term}%',))
        results = c.fetchall()
        conn.close()
        return {"message": f"Search results for '{term}':", 
                "history": [{"sender": r[0], "message": r[1], "timestamp": r[2]} for r in results]}
    except Exception as e:
        return f"Error searching history: {str(e)}"

def handle_backup(type_, source, dest):
    try:
        if os.path.isfile(source):
            shutil.copy2(source, dest)
        else:
            shutil.copytree(source, dest, dirs_exist_ok=True)
        return f"Backed up {type_} from {source} to {dest}"
    except Exception as e:
        return f"Backup error: {str(e)}"

def save_message(sender, message):
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute('INSERT INTO messages (sender, message) VALUES (?, ?)',
              (sender, message))
    conn.commit()
    conn.close()

# Command router
def route_command(command_data):
    try:
        command = command_data.get('command')
        params = command_data.get('params', [])
        
        if not command:
            return "No command specified"
        
        command_handlers = {
            'volume': lambda: handle_volume(params[0]),
            'brightness': lambda: handle_brightness(params[0]),
            'version': lambda: handle_version_check(params[0]),
            'app': lambda: handle_app_check(params[0]),
            'file': lambda: handle_file_operation(params[0], params[1]),
            'folder': lambda: create_folder_in_vscode(params[0], params[1]),
            'code': lambda: handle_code_operation(params[0], params[1]),
            'vscode': lambda: handle_vscode(params[0]),
            'create_path': lambda: handle_create_path(params[0]),
            'history': handle_history,
            'search': lambda: handle_search(params[0]),
            'backup': lambda: handle_backup(params[0], params[1], params[2])
        }
        
        handler = command_handlers.get(command)
        if not handler:
            return f"Command not recognized: {command}"
            
        if not isinstance(params, list):
            return "Invalid params format: must be a list"
            
        return handler()
        
    except Exception as e:
        return f"Error processing command: {str(e)}"

@app.route('/chat', methods=['POST'])
def process_message():
    try:
        message = request.json.get('message')
        if not message:
            return jsonify({"error": "No message provided"}), 400
            
        save_message('User', message)
        
        # Get command interpretation from GPT
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
            # If command interpretation fails, treat as regular chat
            chat_response = chat.send_message(message)
            save_message('Bot', chat_response.text)
            return jsonify({"reply": chat_response.text})
            
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

if __name__ == "__main__":
    app.run(debug=True)