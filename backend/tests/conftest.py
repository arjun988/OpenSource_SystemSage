import pytest
import os
import tempfile
import sqlite3
from unittest.mock import MagicMock


@pytest.fixture(scope="session")
def temp_db_path():
    """Create a temporary database path for testing"""
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)
    yield db_path
    os.unlink(db_path)


@pytest.fixture
def mock_env_vars():
    """Mock environment variables"""
    env_vars = {
        'gemini_gpt_key': 'test_key_123',
        'FLASK_ENV': 'testing'
    }

    with pytest.MonkeyPatch().context() as m:
        for key, value in env_vars.items():
            m.setenv(key, value)
        yield env_vars


@pytest.fixture
def mock_subprocess():
    """Mock subprocess for testing system commands"""
    with pytest.MonkeyPatch().context() as m:
        mock_popen = MagicMock()
        mock_popen.communicate.return_value = (b'output', b'')
        mock_popen.returncode = 0
        m.setattr('subprocess.Popen', mock_popen)
        yield mock_popen


@pytest.fixture
def sample_chat_data():
    """Sample chat data for testing"""
    return [
        {'sender': 'user', 'message': 'Hello'},
        {'sender': 'bot', 'message': 'Hi there!'},
        {'sender': 'user', 'message': 'How are you?'},
        {'sender': 'bot', 'message': 'I am doing well, thank you!'}
    ]


@pytest.fixture
def mock_gemini():
    """Mock Google Gemini AI for testing"""
    mock_model = MagicMock()
    mock_chat = MagicMock()
    mock_chat.send_message.return_value.text = "This is a test response from Gemini."

    with pytest.MonkeyPatch().context() as m:
        m.setattr('google.generativeai.GenerativeModel', MagicMock(return_value=mock_model))
        m.setattr('google.generativeai.GenerativeModel().start_chat', MagicMock(return_value=mock_chat))
        yield mock_chat


@pytest.fixture
def mock_screen_brightness():
    """Mock screen brightness control"""
    mock_sbc = MagicMock()
    mock_sbc.get_brightness.return_value = [75]
    mock_sbc.set_brightness.return_value = None

    with pytest.MonkeyPatch().context() as m:
        import sys
        if 'screen_brightness_control' not in sys.modules:
            sys.modules['screen_brightness_control'] = mock_sbc
        else:
            m.setattr('screen_brightness_control', mock_sbc)
        yield mock_sbc


@pytest.fixture
def mock_psutil():
    """Mock psutil for system monitoring"""
    mock_psutil = MagicMock()

    # Mock CPU
    mock_psutil.cpu_percent.return_value = 45.5

    # Mock memory
    mock_memory = MagicMock()
    mock_memory.percent = 60.2
    mock_psutil.virtual_memory.return_value = mock_memory

    # Mock disk
    mock_disk = MagicMock()
    mock_disk.percent = 75.8
    mock_psutil.disk_usage.return_value = mock_disk

    with pytest.MonkeyPatch().context() as m:
        import sys
        if 'psutil' not in sys.modules:
            sys.modules['psutil'] = mock_psutil
        else:
            m.setattr('psutil', mock_psutil)
        yield mock_psutil


@pytest.fixture
def mock_speech_recognition():
    """Mock speech recognition"""
    mock_sr = MagicMock()
    mock_recognizer = MagicMock()
    mock_microphone = MagicMock()
    mock_audio = MagicMock()

    mock_recognizer.listen.return_value = mock_audio
    mock_recognizer.recognize_google.return_value = "Hello world"

    with pytest.MonkeyPatch().context() as m:
        import sys
        if 'speech_recognition' not in sys.modules:
            sys.modules['speech_recognition'] = mock_sr
        m.setattr('speech_recognition.Recognizer', MagicMock(return_value=mock_recognizer))
        m.setattr('speech_recognition.Microphone', MagicMock(return_value=mock_microphone))
        yield mock_recognizer


@pytest.fixture
def temp_file():
    """Create a temporary file for testing"""
    fd, path = tempfile.mkstemp()
    try:
        with os.fdopen(fd, 'w') as f:
            f.write('temporary file content')
        yield path
    finally:
        os.unlink(path)


@pytest.fixture
def temp_directory():
    """Create a temporary directory for testing"""
    temp_dir = tempfile.mkdtemp()
    try:
        yield temp_dir
    finally:
        import shutil
        shutil.rmtree(temp_dir)
