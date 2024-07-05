import os
import subprocess
from datetime import datetime

# Directory containing blueprint files
blueprint_directory = 'automations'
# Path to the main README.md file
readme_path = 'README.md'
# Directory name to ignore
ignore_folder = 'dev'

def get_last_commit_date(file_path):
    """Get the last commit date for a given file."""
    result = subprocess.run(['git', 'log', '-1', '--format=%cd', '--', file_path],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    # Parse the date to remove time information
    date = datetime.strptime(result.stdout.strip(), '%a %b %d %H:%M:%S %Y %z')
    return date.strftime('%Y-%m-%d')

def get_blueprints(directory, ignore_folder):
    """Retrieve the list of blueprint files in the directory, ignoring specified folders."""
    blueprints = []
    for root, dirs, files in os.walk(directory):
        if ignore_folder not in root.split(os.sep):
            for filename in files:
                if filename.endswith('.yaml'):
                    filepath = os.path.join(root, filename)
                    name = os.path.splitext(filename)[0]
                    formatted_name = ' '.join(word.capitalize() for word in name.split('_'))
                    last_commit_date = get_last_commit_date(filepath)
                    import_url = f"https://my.home-assistant.io/redirect/blueprint_import/?url=https://github.com/asucrews/ha-blueprints/blob/main/{filepath.replace(os.sep, '/')}"
                    shield_url = f"https://img.shields.io/badge/Import%20Blueprint-blue?logo=home-assistant&style=flat-square"
                    blueprints.append((formatted_name, filepath, last_commit_date, import_url, shield_url))
    return blueprints

def update_readme(blueprints, readme_path):
    """Update the README.md file with the list of blueprints."""
    with open(readme_path, 'r') as file:
        lines = file.readlines()

    # Find the section to update
    start_line = None
    end_line = None
    for i, line in enumerate(lines):
        if line.strip() == "## Available Blueprints":
            start_line = i + 1  # Assume the list starts 1 line after the header
        elif start_line and (line.strip().startswith("## ") or i == len(lines) - 1):
            end_line = i
            break

    if start_line is None or end_line is None:
        print("Could not find the Available Blueprints section in README.md")
        return

    # Generate the new content
    blueprint_lines = ['\n']
    for name, path, date, import_url, shield_url in blueprints:
        blueprint_lines.append(f'- [{name}](./{path}) (Last updated: {date}) [![Import Blueprint]({shield_url})]({import_url})\n')
    blueprint_lines.append('\n')

    new_content = lines[:start_line] + blueprint_lines + lines[end_line:]

    # Write the updated content back to the file
    with open(readme_path, 'w') as file:
        file.writelines(new_content)

def main():
    blueprints = get_blueprints(blueprint_directory, ignore_folder)
    blueprints.sort(key=lambda x: x[0])  # Sort blueprints alphabetically
    update_readme(blueprints, readme_path)
    print("README.md updated successfully")

if __name__ == "__main__":
    main()
