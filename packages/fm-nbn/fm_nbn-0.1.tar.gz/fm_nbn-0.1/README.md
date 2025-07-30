# Folder Utils

A simple Python library for folder and file manipulation using an object-oriented approach.

## Installation

You can install this library locally by running the following command in the root directory (`my_folder_lib/`):

```
pip install -e .
```

## Usage

```python
from folder_utils import FolderManager

# Create an instance of FolderManager
fm = FolderManager()

# Create a folder
fm.create_folder("my_directory")

# List files in the folder (optionally filter by extension)
files = fm.list_files("my_directory", extension_filter=".txt")
print(files)

# Copy a file
fm.copy_file("source.txt", "destination.txt")

# Move a file
fm.move_file("destination.txt", "new_location.txt")

# Delete a folder
fm.delete_folder("my_directory")
```

## Features

- Create folders
- Delete folders
- List files in a folder with optional extension filtering
- Copy files
- Move files

## Requirements

- Python 3.6 or higher

## Publishing to Git Repository

To push this library to a remote Git repository (e.g., GitHub):

1. Create a new repository on GitHub or your preferred Git hosting service.
2. Run the following commands in the `my_folder_lib/` directory:

   ```
   git remote add origin <repository-url>
   git branch -M main
   git push -u origin main
   ```

   Replace `<repository-url>` with the URL of your remote repository.

## Publishing to PyPI

To publish this library to PyPI so others can install it via `pip`:

1. Ensure you have the necessary tools installed:

   ```
   pip install build twine
   ```

2. Build the distribution packages:

   ```
   python -m build
   ```

3. Upload to PyPI (you'll need a PyPI account and API token):

   ```
   python -m twine upload dist/*
   ```

   Follow the prompts to enter your PyPI credentials or API token.

After publishing, users can install your library with:

```
pip install folder-utils
