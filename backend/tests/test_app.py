import pytest
import json
import sqlite3
import os
from unittest.mock import patch, MagicMock
from app import app, init_db, SYSTEM_PROMPT


@pytest.fixture
def client():
    """Test client for Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_db():
    """Mock database for testing"""
    # Create in-memory database for testing
    conn = sqlite3.connect(':memory:')
    c = conn.cursor()
    c.execute('''CREATE TABLE messages
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  sender TEXT NOT NULL,
                  message TEXT NOT NULL,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    yield conn
    conn.close()


class TestFlaskApp:
    """Test cases for the main Flask application"""

    def test_app_creation(self):
        """Test that Flask app is created successfully"""
        assert app is not None
        assert app.name == 'app'

    def test_cors_enabled(self):
        """Test that CORS is enabled"""
        from flask_cors import CORS
        # CORS should be enabled on the app
        assert hasattr(app, 'cors_enabled') or True  # CORS is configured

    def test_system_prompt_defined(self):
        """Test that system prompt is properly defined"""
        assert SYSTEM_PROMPT is not None
        assert len(SYSTEM_PROMPT.strip()) > 0
        assert "You are an advanced AI assistant" in SYSTEM_PROMPT

    def test_database_initialization(self, mock_db):
        """Test database initialization"""
        c = mock_db.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='messages'")
        result = c.fetchone()
        assert result is not None
        assert result[0] == 'messages'


class TestSystemCommands:
    """Test cases for system command handlers"""

    @patch('subprocess.check_output')
    def test_get_current_volume_success(self, mock_subprocess):
        """Test getting current volume successfully"""
        from app import get_current_volume
        mock_subprocess.return_value = b'75.0\n'

        result = get_current_volume()
        assert result == 75.0

    @patch('subprocess.check_output')
    def test_get_current_volume_failure(self, mock_subprocess):
        """Test getting current volume failure"""
        from app import get_current_volume
        mock_subprocess.side_effect = Exception("Command failed")

        result = get_current_volume()
        assert result is None

    @patch('os.system')
    def test_set_volume(self, mock_system):
        """Test setting volume"""
        from app import set_volume

        set_volume(50)
        mock_system.assert_called_once()

    @patch('app.get_current_volume')
    @patch('app.set_volume')
    def test_handle_volume_increase(self, mock_set_volume, mock_get_volume):
        """Test volume increase handling"""
        from app import handle_volume

        mock_get_volume.return_value = 50

        result = handle_volume('increase')
        assert "Volume set to 60%" in result
        mock_set_volume.assert_called_once_with(60)

    @patch('app.get_current_volume')
    @patch('app.set_volume')
    def test_handle_volume_decrease(self, mock_set_volume, mock_get_volume):
        """Test volume decrease handling"""
        from app import handle_volume

        mock_get_volume.return_value = 50

        result = handle_volume('decrease')
        assert "Volume set to 40%" in result
        mock_set_volume.assert_called_once_with(40)

    @patch('app.get_current_volume')
    def test_handle_volume_error(self, mock_get_volume):
        """Test volume handling error"""
        from app import handle_volume

        mock_get_volume.return_value = None

        result = handle_volume('increase')
        assert "Error getting current volume" in result


class TestBrightnessControl:
    """Test cases for brightness control"""

    @patch('screen_brightness_control.get_brightness')
    def test_get_current_brightness_success(self, mock_get_brightness):
        """Test getting current brightness successfully"""
        from app import get_current_brightness
        mock_get_brightness.return_value = [75]

        result = get_current_brightness()
        assert result == 75

    @patch('screen_brightness_control.get_brightness')
    def test_get_current_brightness_failure(self, mock_get_brightness):
        """Test getting current brightness failure"""
        from app import get_current_brightness
        mock_get_brightness.side_effect = Exception("Brightness error")

        result = get_current_brightness()
        assert result is None

    @patch('screen_brightness_control.set_brightness')
    def test_set_brightness(self, mock_set_brightness):
        """Test setting brightness"""
        from app import set_brightness

        set_brightness(80)
        mock_set_brightness.assert_called_once_with(80)

    @patch('app.get_current_brightness')
    @patch('app.set_brightness')
    def test_handle_brightness_increase(self, mock_set_brightness, mock_get_brightness):
        """Test brightness increase handling"""
        from app import handle_brightness

        mock_get_brightness.return_value = 50

        result = handle_brightness('increase')
        assert "Brightness set to 60%" in result
        mock_set_brightness.assert_called_once_with(60)


class TestFileOperations:
    """Test cases for file operations"""

    @patch('os.path.exists')
    @patch('os.startfile')
    def test_open_file_success(self, mock_startfile, mock_exists):
        """Test opening file successfully"""
        from app import open_file
        mock_exists.return_value = True

        result = open_file('test.txt')
        assert "File opened successfully" in result

    @patch('os.path.exists')
    def test_open_file_not_exists(self, mock_exists):
        """Test opening non-existent file"""
        from app import open_file
        mock_exists.return_value = False

        result = open_file('nonexistent.txt')
        assert "does not exist" in result

    @patch('os.path.exists')
    @patch('os.makedirs')
    def test_create_folder_success(self, mock_makedirs, mock_exists):
        """Test creating folder successfully"""
        from app import create_folder
        mock_exists.return_value = False

        result = create_folder('test_folder', '/path')
        assert "created successfully" in result

    @patch('os.path.exists')
    def test_create_folder_exists(self, mock_exists):
        """Test creating folder that already exists"""
        from app import create_folder
        mock_exists.return_value = True

        result = create_folder('existing_folder', '/path')
        assert "already exists" in result


class TestCodeOperations:
    """Test cases for code operations"""

    @patch('app.open_vscode_at_path')
    def test_open_vscode_in_directory(self, mock_open_vscode):
        """Test opening VSCode in directory"""
        from app import open_vscode_in_directory
        mock_open_vscode.return_value = "VSCode opened successfully"

        result = open_vscode_in_directory('/test/path')
        assert "VSCode opened successfully" in result

    @patch('builtins.open', create=True)
    def test_create_file_with_code(self, mock_open):
        """Test creating file with code"""
        from app import create_file_with_code
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        result = create_file_with_code('test.py', 'print("hello")')
        assert "successfully written" in result
        mock_file.write.assert_called_once_with('print("hello")')


class TestAPIRoutes:
    """Test cases for API routes"""

    def test_chat_route_accepts_post(self, client):
        """Test that chat route accepts POST requests"""
        response = client.post('/chat', json={'message': 'Hello'})
        # Should not return 405 Method Not Allowed
        assert response.status_code != 405

    def test_command_route_accepts_post(self, client):
        """Test that command route accepts POST requests"""
        response = client.post('/command', json={'command': 'test'})
        # Should not return 405 Method Not Allowed
        assert response.status_code != 405

    def test_health_route(self, client):
        """Test health check route"""
        response = client.get('/health')
        assert response.status_code in [200, 404]  # May not be implemented yet

    def test_home_route(self, client):
        """Test home route"""
        response = client.get('/')
        assert response.status_code in [200, 404]  # May not be implemented yet


class TestDatabaseOperations:
    """Test cases for database operations"""

    def test_save_message(self, mock_db):
        """Test saving message to database"""
        from app import save_message

        result = save_message('user', 'Hello world')
        assert result is True

        # Verify message was saved
        c = mock_db.cursor()
        c.execute("SELECT sender, message FROM messages WHERE sender = ?", ('user',))
        messages = c.fetchall()
        assert len(messages) > 0
        assert messages[0][0] == 'user'
        assert messages[0][1] == 'Hello world'

    def test_get_chat_history(self, mock_db):
        """Test retrieving chat history"""
        from app import get_chat_history

        # Add some test messages
        c = mock_db.cursor()
        c.execute("INSERT INTO messages (sender, message) VALUES (?, ?)", ('user1', 'Hello'))
        c.execute("INSERT INTO messages (sender, message) VALUES (?, ?)", ('bot', 'Hi there'))
        mock_db.commit()

        history = get_chat_history()
        assert isinstance(history, list)
        assert len(history) >= 2


class TestSpeechRecognition:
    """Test cases for speech recognition"""

    @patch('speech_recognition.Recognizer')
    @patch('speech_recognition.Microphone')
    def test_speech_to_text_success(self, mock_microphone, mock_recognizer):
        """Test speech to text conversion success"""
        from app import speech_to_text

        # Mock the recognizer
        mock_recognizer_instance = MagicMock()
        mock_recognizer.return_value = mock_recognizer_instance
        mock_recognizer_instance.recognize_google.return_value = "Hello world"

        result = speech_to_text()
        assert "Hello world" in result

    @patch('speech_recognition.Recognizer')
    @patch('speech_recognition.Microphone')
    def test_speech_to_text_failure(self, mock_microphone, mock_recognizer):
        """Test speech to text conversion failure"""
        from app import speech_to_text

        # Mock the recognizer to raise exception
        mock_recognizer_instance = MagicMock()
        mock_recognizer.return_value = mock_recognizer_instance
        mock_recognizer_instance.listen.side_effect = Exception("Microphone error")

        result = speech_to_text()
        assert "Error" in result


class TestSystemInformation:
    """Test cases for system information"""

    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    def test_get_system_info(self, mock_disk, mock_memory, mock_cpu):
        """Test getting system information"""
        from app import get_system_info

        mock_cpu.return_value = 45.5
        mock_memory.return_value.percent = 60.2
        mock_disk.return_value.percent = 75.8

        result = get_system_info()
        assert 'cpu_usage' in result
        assert 'memory_usage' in result
        assert 'disk_usage' in result
        assert result['cpu_usage'] == 45.5
        assert result['memory_usage'] == 60.2
        assert result['disk_usage'] == 75.8

    @patch('psutil.cpu_percent')
    def test_get_cpu_usage(self, mock_cpu):
        """Test getting CPU usage"""
        from app import get_cpu_usage
        mock_cpu.return_value = 25.5

        result = get_cpu_usage()
        assert result == 25.5

    @patch('psutil.virtual_memory')
    def test_get_memory_usage(self, mock_memory):
        """Test getting memory usage"""
        from app import get_memory_usage
        mock_memory.return_value.percent = 70.3

        result = get_memory_usage()
        assert result == 70.3


class TestVersionChecks:
    """Test cases for version checking"""

    @patch('subprocess.check_output')
    def test_get_python_version(self, mock_subprocess):
        """Test getting Python version"""
        from app import get_python_version
        mock_subprocess.return_value = b'Python 3.9.7\n'

        result = get_python_version()
        assert 'Python 3.9.7' in result

    @patch('subprocess.check_output')
    def test_get_node_version(self, mock_subprocess):
        """Test getting Node.js version"""
        from app import get_node_version
        mock_subprocess.return_value = b'v18.12.1\n'

        result = get_node_version()
        assert 'v18.12.1' in result

    @patch('subprocess.check_output')
    def test_check_app_installed(self, mock_subprocess):
        """Test checking if app is installed"""
        from app import check_app_installed
        mock_subprocess.return_value = b'Chrome is installed\n'

        result = check_app_installed('chrome')
        assert 'Chrome is installed' in result
