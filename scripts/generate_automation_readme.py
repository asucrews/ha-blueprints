import os
import subprocess
from datetime import datetime

# Directory containing blueprint files
blueprint_directory = 'automations'
# Path to the main README.md file
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
                    import_url = f"https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https://github.com/asucrews/ha-blueprints/blob/main/{yaml_path.replace(os.sep, '/')}"
                    shield_url = f"https://img.shields.io/badge/Import%20Blueprint-blue?logo=home-assistant&style=flat-square"
                    blueprints.append((dir_name, readme_path, last_commit_date, import_url, shield_url))
    return blueprints

def generate_readme_content(blueprints):
    """Generate the full content for README.md."""
    readme_lines = [
        "# Home Assistant Blueprints\n",
        "\n",
        "Welcome to the **Home Assistant Blueprints** repository! This collection of automation blueprints is created by **asucrews** to help you set up automations for various Home Assistant setups. Each blueprint is designed to simplify and enhance your Home Assistant experience.\n",
        "\n",
        "## Available Blueprints\n",
        "\n"
    ]

    for name, path, date, import_url, shield_url in blueprints:
        readme_lines.append(f'- [{name}](./{path}) (Last updated: {date}) [![Import Blueprint]({shield_url})]({import_url})\n')
    
    readme_lines.extend([
        "\n",
        "## Usage\n",
        "\n",
        "1. **Select a Blueprint:** Browse the list of available blueprints and select the one that matches your needs.\n",
        "2. **Copy the YAML:** Click on the blueprint link to view the YAML file. Copy the YAML content.\n",
        "3. **Import into Home Assistant:** In Home Assistant, navigate to `Configuration > Blueprints` and click on \"Import Blueprint\". Paste the YAML content and save.\n",
        "4. **Create Automation:** Use the imported blueprint to create a new automation and configure it as needed.\n",
        "\n",
        "## Contributions\n",
        "We welcome contributions to this repository! If you would like to add new blueprints or improve existing ones, please follow the guidelines provided in the [repository](https://github.com/asucrews/ha-blueprints).\n"
    ])
    
    return readme_lines

def update_readme(blueprints, readme_path):
    """Update the README.md file with the new content."""
    readme_content = generate_readme_content(blueprints)

    # Write the updated content back to the file
    with open(readme_path, 'w') as file:
        file.writelines(readme_content)

def main():
    blueprints = get_blueprints(blueprint_directory, ignore_folder)
    blueprints.sort(key=lambda x: x[0])  # Sort blueprints alphabetically
    update_readme(blueprints, readme_path)
    print("README.md updated successfully")

if __name__ == "__main__":
    main()
