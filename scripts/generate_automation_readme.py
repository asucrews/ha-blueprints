import os
import subprocess
from datetime import datetime

# Directory containing blueprint files
blueprint_directory = 'automations'
# Path to the README.md file in the automations directory
readme_path = 'automations/README.md'
# Directory name to ignore
ignore_folder = 'dev'

def get_last_commit_date(file_path):
    """Get the last commit date for a given file."""
    result = subprocess.run(['git', 'log', '-1', '--format=%cd', '--', file_path],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    # Parse the date to remove time information
    date = datetime.strptime(result.stdout.strip(), '%a %b %d %H:%M:%S %Y %z')
    return date.strftime('%Y-%m-%d')

def get_blueprint_description(directory):
    """Retrieve the first few lines of the README.md file for the blueprint description."""
    readme_path = os.path.join(directory, 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r') as readme_file:
            lines = readme_file.readlines()
            # Get the first few lines as the description
            description_lines = lines[:5]
            description = ''.join(description_lines).strip()
            return description
    return "No description available."

def get_blueprints(directory, ignore_folder):
    """Retrieve the list of blueprint files in the directory, ignoring specified folders."""
    blueprints = []
    base_url = "https://github.com/asucrews/ha-blueprints/blob/main/"
    import_base_url = "https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url="

    for root, _, files in os.walk(directory):
        if ignore_folder not in root.split(os.sep):
            for filename in files:
                if filename.endswith('.yaml'):
                    filepath = os.path.join(root, filename)
                    name = os.path.splitext(filename)[0]
                    formatted_name = ' '.join(word.capitalize() for word in name.split('_'))
                    last_commit_date = get_last_commit_date(filepath)
                    blueprint_url = f"{base_url}{filepath.replace(os.sep, '/')}"
                    import_url = f"{import_base_url}{blueprint_url}"
                    description = get_blueprint_description(root)
                    blueprints.append({
                        "name": formatted_name,
                        "blueprint_url": blueprint_url,
                        "import_url": import_url,
                        "last_commit_date": last_commit_date,
                        "description": description
                    })
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
            start_line = i + 2  # Assume the list starts 2 lines after the header
        elif start_line and line.strip() == "## Usage":
            end_line = i
            break

    if start_line is None or end_line is None:
        print("Could not find the available blueprints section in README.md")
        return

    # Generate the new content
    blueprint_lines = [
        f"### [{blueprint['name']}]({blueprint['blueprint_url']})\n"
        f"[![Import Blueprint](https://my.home-assistant.io/badges/blueprint_import.svg)]({blueprint['import_url']})\n\n"
        f"{blueprint['description']} (Last updated: {blueprint['last_commit_date']})\n"
        for blueprint in blueprints
    ]
    new_content = lines[:start_line] + blueprint_lines + ["\n"] + lines[end_line:]

    # Write the updated content back to the file
    with open(readme_path, 'w') as file:
        file.writelines(new_content)

def main():
    blueprints = get_blueprints(blueprint_directory, ignore_folder)
    update_readme(blueprints, readme_path)
    print("README.md updated successfully")

if __name__ == "__main__":
    main()
