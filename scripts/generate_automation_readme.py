import os

def generate_readme():
    base_url = "https://github.com/asucrews/ha-blueprints/blob/main/automations/"
    import_base_url = "https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url="
    readme_content = """# Home Assistant Blueprints

Welcome to the **Home Assistant Blueprints** repository! This collection of automation blueprints is created by **asucrews** to help you set up automations for various Home Assistant setups. Each blueprint is designed to simplify and enhance your Home Assistant experience.

## Available Blueprints
"""

    for root, dirs, files in os.walk("automations"):
        # Skip 'dev' folders
        if 'dev' in root.split(os.sep):
            continue
        for file in files:
            if file.endswith(".yaml"):
                blueprint_path = os.path.join(root, file)
                blueprint_name = os.path.splitext(file)[0].replace('_', ' ').title()
                blueprint_url = base_url + blueprint_path.replace("\\", "/")
                import_url = import_base_url + blueprint_url

                readme_content += f"""
### [{blueprint_name}]({blueprint_url})
[![Import Blueprint](https://my.home-assistant.io/badges/blueprint_import.svg)]({import_url})

Description for {blueprint_name} blueprint.
---
"""

    readme_content += """
## Usage

1. **Select a Blueprint:** Browse the list of available blueprints and select the one that matches your needs.
2. **Copy the YAML:** Click on the blueprint link to view the YAML file. Copy the YAML content.
3. **Import into Home Assistant:** In Home Assistant, navigate to `Configuration > Blueprints` and click on "Import Blueprint". Paste the YAML content and save.
4. **Create Automation:** Use the imported blueprint to create a new automation and configure it as needed.

## Contributions

We welcome contributions to this repository! If you would like to add new blueprints or improve existing ones, please follow the guidelines provided in the [repository](https://github.com/asucrews/ha-blueprints).
"""

    with open("automations/README.md", "w") as f:
        f.write(readme_content)

if __name__ == "__main__":
    generate_readme()
