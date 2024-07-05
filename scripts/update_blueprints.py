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
    for root, _, files in os.walk(directory):
        if ignore_folder not in root.split(os.sep):
            for filename in files:
                if filename.endswith('.yaml'):
                    filepath = os.path.join(root, filename)
                    name = os.path.splitext(filename)[0]
                    formatted_name = ' '.join(word.capitalize() for word in name.split('_'))
                    last_commit_date = get_last_commit_date(filepath)
                    readme_url = f"https://github.com/asucrews/ha-blueprints/blob/main/{root}/README.md"
                    blueprints.append(f"- [{formatted_name}]({readme_url}) (Last updated: {last_commit_date})")
    return blueprints

def generate_readme(blueprints, readme_path):
    """Generate the entire README.md file with the list of blueprints."""
    header = "# ha-blueprints\n\nBlueprints for Home Assistant\n\n"
    stats = (
        "## Stats\n\n"
        "![Min HA Version](https://img.shields.io/badge/Min%20HA%20Version-2024.6.0-blue?style=flat&logo=home-assistant&color=blue)\n"
        "[![HA Blueprint Exchange](https://img.shields.io/badge/HA%20Blueprint%20Exchange-Topics-blue?style=flat&logo=home-assistant&color=blue)](https://community.home-assistant.io/c/blueprints-exchange/53)\n\n"
        "[![GitHub License](https://img.shields.io/github/license/asucrews/ha-blueprints?style=flat&logo=github&color=blue)](LICENSE.md)\n"
        "[![GitHub Discussions](https://img.shields.io/github/discussions/asucrews/ha-blueprints?style=flat&logo=github&color=blue)](https://github.com/asucrews/ha-blueprints/discussions)\n"
        "![GitHub last commit](https://img.shields.io/github/last-commit/asucrews/ha-blueprints?style=flat&logo=github&color=blue)\n"
        "![GitHub commit activity](https://img.shields.io/github/commit-activity/m/asucrews/ha-blueprints?style=flat&logo=github&color=blue)\n"
        "![GitHub commit activity](https://img.shields.io/github/commit-activity/y/asucrews/ha-blueprints?style=flat&logo=github&color=blue)\n\n"
    )
    intro = "## Automation Blueprints\n\n"
    doc_link = "Check out the [automations documentation](https://github.com/asucrews/ha-blueprints/blob/main/automations/README.md) for detailed instructions and examples.\n\n"
    feedback = (
        "## Feedback\n\n"
        "We value your input and welcome any feedback or suggestions you may have regarding the Blueprints. "
        "Your feedback helps us continually improve and refine our offerings for the community.\n\n"
        "Please feel free to leave your comments below or reach out to us on the [Home Assistant forum](https://community.home-assistant.io/). "
        "Thank you for your support!\n"
    )

    blueprint_lines = [f"{blueprint}\n" for blueprint in blueprints]
    content = header + stats + intro + doc_link + ''.join(blueprint_lines) + "\n" + feedback

    # Write the generated content to the README.md file
    with open(readme_path, 'w') as file:
        file.write(content)

def main():
    blueprints = get_blueprints(blueprint_directory, ignore_folder)
    blueprints.sort(key=lambda x: x[0])  # Sort blueprints alphabetically
    generate_readme(blueprints, readme_path)
    print("README.md generated successfully")

if __name__ == "__main__":
    main()
