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
        # Skip 'dev' folder
        if ignore_folder in root.split(os.sep):
            continue

        for dir_name in dirs:
            blueprint_dir = os.path.join(root, dir_name)
            readme_path = os.path.join(blueprint_dir, 'README.md')
            if os.path.isfile(readme_path):
                yaml_files = [f for f in os.listdir(blueprint_dir) if f.endswith('.yaml')]
                if yaml_files:
                    yaml_file = yaml_files[0]  # Assuming there is only one YAML file per blueprint directory
                    yaml_path = os.path.join(blueprint_dir, yaml_file)
                    last_commit_date = get_last_commit_date(readme_path)
                    import_url = f"https://my.home-assistant.io/redirect/blueprint_import/?url=https://github.com/asucrews/ha-blueprints/blob/main/{yaml_path.replace(os.sep, '/')}"
                    shield_url = f"https://img.shields.io/badge/Import%20Blueprint-blue?logo=home-assistant&style=flat-square"
                    blueprints.append((dir_name, readme_path, last_commit_date, import_url, shield_url))
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
        elif start_line and line.strip().startswith("## "):
            end_line = i
            break
    if end_line is None:
        end_line = len(lines)

    if start_line is None:
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

    print(new_content)

def main():
    blueprints = get_blueprints(blueprint_directory, ignore_folder)
    blueprints.sort(key=lambda x: x[0])  # Sort blueprints alphabetically
    update_readme(blueprints, readme_path)
    print("README.md updated successfully")

if __name__ == "__main__":
    main()
