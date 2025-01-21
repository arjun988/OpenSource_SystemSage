# code_editor.py

import os

def open_vscode():
    try:
        os.system("code .")  # This command opens VSCode in the current directory.
        return "VSCode opened successfully."
    except Exception as e:
        return f"An error occurred while opening VSCode: {str(e)}"
    
def open_vscode_at_path(path):
    try:
        # Handle spaces in the path by enclosing it in quotes
        if os.path.exists(path):
            os.system(f'code "{path}"')  # Open VSCode at the specified path.
            return f"VSCode opened at path '{path}' successfully."
        else:
            return f"The specified path '{path}' does not exist."
    except Exception as e:
        return f"An error occurred while opening VSCode at path '{path}': {str(e)}"

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

def write_code_to_file(code, file_path):
    try:
        with open(file_path, 'w') as file:
            file.write(code)
        return f"Code successfully written to {file_path}."
    except Exception as e:
        return f"An error occurred while writing to {file_path}: {str(e)}"