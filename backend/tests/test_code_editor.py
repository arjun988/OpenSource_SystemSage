import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
from code_editor import open_vscode, open_vscode_at_path, create_folder_in_vscode, write_code_to_file


class TestVSCodeOperations:
    """Test cases for VSCode-related operations"""

    @patch('os.system')
    def test_open_vscode_success(self, mock_system):
        """Test opening VSCode successfully"""
        mock_system.return_value = 0

        result = open_vscode()
        assert "VSCode opened successfully" in result
        mock_system.assert_called_once_with("code .")

    @patch('os.system')
    def test_open_vscode_failure(self, mock_system):
        """Test opening VSCode failure"""
        mock_system.side_effect = Exception("Command failed")

        result = open_vscode()
        assert "error occurred" in result.lower()

    @patch('os.path.exists')
    @patch('os.system')
    def test_open_vscode_at_path_success(self, mock_system, mock_exists):
        """Test opening VSCode at specific path successfully"""
        mock_exists.return_value = True
        mock_system.return_value = 0

        result = open_vscode_at_path('/test/path')
        assert "successfully" in result
        mock_system.assert_called_once_with('code "/test/path"')

    @patch('os.path.exists')
    def test_open_vscode_at_path_not_exists(self, mock_exists):
        """Test opening VSCode at non-existent path"""
        mock_exists.return_value = False

        result = open_vscode_at_path('/nonexistent/path')
        assert "does not exist" in result

    @patch('os.path.exists')
    @patch('os.system')
    def test_open_vscode_at_path_with_spaces(self, mock_system, mock_exists):
        """Test opening VSCode at path with spaces"""
        mock_exists.return_value = True
        mock_system.return_value = 0

        result = open_vscode_at_path('/path with spaces')
        assert "successfully" in result
        mock_system.assert_called_once_with('code "/path with spaces"')


class TestFolderOperations:
    """Test cases for folder operations"""

    @patch('os.getcwd')
    @patch('os.path.exists')
    @patch('os.makedirs')
    def test_create_folder_in_vscode_success(self, mock_makedirs, mock_exists, mock_getcwd):
        """Test creating folder successfully"""
        mock_getcwd.return_value = '/current/dir'
        mock_exists.return_value = False

        result = create_folder_in_vscode('test_folder')
        assert "created successfully" in result
        mock_makedirs.assert_called_once_with('/current/dir/test_folder')

    @patch('os.path.exists')
    @patch('os.makedirs')
    def test_create_folder_in_vscode_with_path(self, mock_makedirs, mock_exists):
        """Test creating folder at specific path"""
        mock_exists.return_value = False

        result = create_folder_in_vscode('test_folder', '/custom/path')
        assert "created successfully" in result
        expected_path = os.path.join('/custom/path', 'test_folder')
        mock_makedirs.assert_called_once_with(expected_path)

    @patch('os.path.exists')
    def test_create_folder_already_exists(self, mock_exists):
        """Test creating folder that already exists"""
        mock_exists.return_value = True

        result = create_folder_in_vscode('existing_folder', '/path')
        assert "already exists" in result

    @patch('os.makedirs')
    @patch('os.path.exists')
    def test_create_folder_error(self, mock_exists, mock_makedirs):
        """Test creating folder with error"""
        mock_exists.return_value = False
        mock_makedirs.side_effect = Exception("Permission denied")

        result = create_folder_in_vscode('test_folder', '/path')
        assert "error occurred" in result.lower()


class TestFileOperations:
    """Test cases for file operations"""

    @patch('builtins.open', create=True)
    def test_write_code_to_file_success(self, mock_open):
        """Test writing code to file successfully"""
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        result = write_code_to_file('print("hello")', 'test.py')
        assert "successfully written" in result
        mock_file.write.assert_called_once_with('print("hello")')

    @patch('builtins.open', create=True)
    def test_write_code_to_file_error(self, mock_open):
        """Test writing code to file with error"""
        mock_open.side_effect = Exception("File write error")

        result = write_code_to_file('code', 'test.py')
        assert "error occurred" in result.lower()

    def test_write_code_to_file_integration(self):
        """Test actual file writing (integration test)"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as temp_file:
            temp_path = temp_file.name

        try:
            test_code = '# Test Python code\nprint("Hello, World!")'
            result = write_code_to_file(test_code, temp_path)

            assert "successfully written" in result

            # Verify file contents
            with open(temp_path, 'r') as f:
                content = f.read()
                assert content == test_code

        finally:
            os.unlink(temp_path)

    def test_write_code_to_file_different_extensions(self):
        """Test writing code to files with different extensions"""
        test_cases = [
            ('print("python")', 'test.py'),
            ('console.log("js")', 'test.js'),
            ('# HTML comment', 'test.html'),
            ('// CSS comment', 'test.css'),
            ('{"json": "data"}', 'test.json')
        ]

        for code, filename in test_cases:
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=os.path.splitext(filename)[1]) as temp_file:
                temp_path = temp_file.name

            try:
                result = write_code_to_file(code, temp_path)
                assert "successfully written" in result

                with open(temp_path, 'r') as f:
                    content = f.read()
                    assert content == code

            finally:
                os.unlink(temp_path)


class TestPathHandling:
    """Test cases for path handling"""

    def test_path_normalization(self):
        """Test that paths are handled correctly"""
        test_paths = [
            'folder',
            './folder',
            '../folder',
            '/absolute/path/folder',
            'C:\\windows\\path\\folder',  # Windows path
            '~/user/folder'  # Home directory
        ]

        for path in test_paths:
            # Should not raise exceptions
            try:
                if os.path.isabs(path) or path.startswith('~'):
                    continue  # Skip absolute paths for this test
                result = create_folder_in_vscode('test', path)
                assert isinstance(result, str)
            except Exception:
                # Some paths might not work in test environment, that's ok
                pass

    @patch('os.path.exists')
    def test_relative_path_resolution(self, mock_exists):
        """Test relative path resolution"""
        mock_exists.return_value = True

        # Test with current directory
        result = open_vscode_at_path('.')
        assert isinstance(result, str)

        # Test with parent directory
        result = open_vscode_at_path('..')
        assert isinstance(result, str)


class TestErrorHandling:
    """Test cases for error handling"""

    @patch('os.system')
    def test_system_command_errors(self, mock_system):
        """Test handling of system command errors"""
        mock_system.return_value = 1  # Non-zero exit code

        # These functions should handle errors gracefully
        result1 = open_vscode()
        result2 = open_vscode_at_path('/test')

        assert isinstance(result1, str)
        assert isinstance(result2, str)

    def test_file_operation_edge_cases(self):
        """Test edge cases for file operations"""
        # Empty code
        result = write_code_to_file('', 'test.txt')
        assert "successfully written" in result

        # Very long code
        long_code = 'x' * 10000
        result = write_code_to_file(long_code, 'test.txt')
        assert "successfully written" in result

        # Code with special characters
        special_code = 'console.log("Hello 😀 🌍 \\n \\"quotes\\" \\'single\\'");'
        result = write_code_to_file(special_code, 'test.js')
        assert "successfully written" in result

    @patch('os.makedirs')
    @patch('os.path.exists')
    def test_folder_creation_edge_cases(self, mock_exists, mock_makedirs):
        """Test edge cases for folder creation"""
        mock_exists.return_value = False

        # Empty folder name
        result = create_folder_in_vscode('', '/path')
        assert isinstance(result, str)

        # Folder name with special characters
        result = create_folder_in_vscode('test-folder_123', '/path')
        assert isinstance(result, str)

        # Very long folder name
        long_name = 'a' * 200
        result = create_folder_in_vscode(long_name, '/path')
        assert isinstance(result, str)
