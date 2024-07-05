import os
import subprocess
from datetime import datetime
import urllib.parse

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

def generate_shield_url(label, message, color):
    """Generate a shields.io URL for a custom badge."""
    label = urllib.parse.quote(label)
    message = urllib.parse.quote(message)
    color = urllib.parse.quote(color)
    return f"https://img.shields.io/badge/{label}-{message}-{color}"

def get_blueprints(directory, ignore_folder):
    """Retrieve the list of blueprint files in the directory, ignoring specified folders."""
    blueprints = []
    for root, _, files in os.walk(directory):
        if ignore_folder not in root.split(os.sep):
            for filename in files:
                if filename.endswith('.yaml'):
                    filepath = os.path.join(root, filename)
                    name = os.path.splitext(filename)[0]
                    formatted_name = ' '.join(word.capitalize() for word in name.split('_'))
                    last_commit_date = get_last_commit_date(filepath)
                    shield_url = generate_shield_url("Last updated", last_commit_date, "blue")
                    readme_url = f"https://github.com/asucrews/ha-blueprints/blob/main/{root}/{name}/README.md"
                    print(f"File: {filename}, Last Commit Date: {last_commit_date}, Shield URL: {shield_url}, README URL: {readme_url}")  # Debug print statement
                    blueprints.append(f"- {formatted_name} [![Last updated]({shield_url})]({readme_url})")
    return blueprints

def update_readme(blueprints, readme_path):
    """Update the README.md file with the list of blueprints."""
    with open(readme_path, 'r') as file:
        lines = file.readlines()

    # Find the section to update
    start_line = None
    end_line = None
    for i, line in enumerate(lines):
        if line.strip() == "## Automation Blueprints":
            start_line = i + 2  # Assume the list starts 2 lines after the header
        elif start_line and line.strip() == "## Feedback":
            end_line = i
            break

    if start_line is None or end_line is None:
        print("Could not find the automation blueprints section in README.md")
        return

    # Generate the new content
    doc_link = "Check out the [automations documentation](https://github.com/asucrews/ha-blueprints/blob/main/automations/README.md) for detailed instructions and examples.\n\n"
    blueprint_lines = [f"{blueprint}\n" for blueprint in blueprints]
    new_content = lines[:start_line] + [doc_link] + blueprint_lines + ["\n"] + lines[end_line:]

    # Write the updated content back to the file
    with open(readme_path, 'w') as file:
        file.writelines(new_content)

def main():
    blueprints = get_blueprints(blueprint_directory, ignore_folder)
    update_readme(blueprints, readme_path)
    print("README.md updated successfully")

if __name__ == "__main__":
    main()

