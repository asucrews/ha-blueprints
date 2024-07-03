import yaml
import sys
import os

def yaml_to_markdown(yaml_file, markdown_file):
    with open(yaml_file, 'r') as f:
        data = yaml.safe_load(f)

    with open(markdown_file, 'w') as f:
        f.write(f"# {data['blueprint']['name']}\n\n")
        f.write(f"## Description\n{data['blueprint']['description']}\n\n")
        f.write(f"## Source\n[{data['blueprint']['source_url']}]({data['blueprint']['source_url']})\n\n")
        f.write(f"## Domain\n{data['blueprint']['domain']}\n\n")
        f.write(f"## Home Assistant Minimum Version\n{data['blueprint']['homeassistant']['min_version']}\n\n")
        
        f.write(f"## Inputs\n\n")
        
        for section in ['required_entities', 'optional_entities']:
            if section in data['blueprint']['input']:
                f.write(f"### {data['blueprint']['input'][section]['name']}\n")
                f.write(f"{data['blueprint']['input'][section]['description']}\n\n")
                for key, value in data['blueprint']['input'][section]['input'].items():
                    f.write(f"- **{value['name']}**\n")
                    f.write(f"  - **Description**: {value['description']}\n")
                    if 'default' in value:
                        f.write(f"  - **Default**: {value['default']}\n")
                    if 'selector' in value:
                        f.write(f"  - **Selector**: `{value['selector']}`\n")
                    f.write("\n")

        f.write("## Variables\n")
        for key, value in data['variables'].items():
            f.write(f"- `{key}`: {value}\n")

        f.write("\n## Triggers\n")
        for trigger in data['trigger']:
            f.write(f"- **{trigger['id']}**: Triggered when the {trigger['platform']} changes from `{trigger['from']}` to `{trigger['to']}`.\n")

        f.write("\n## Actions\n")
        for action in data['action']:
            f.write(f"### {action['choose']['conditions'][0]['id']}\n")
            for step in action['sequence']:
                f.write(f"- **{step['service']}**: {step['data']}\n")

        f.write("\n## Mode\n")
        f.write(f"- **Mode**: {data['mode']}\n")
        f.write(f"- **Max Exceeded**: {data['max_exceeded']}\n")

if __name__ == "__main__":
    yaml_file = sys.argv[1]
    output_dir = os.path.dirname(yaml_file)
    markdown_file = os.path.join(output_dir, 'README.md')
    yaml_to_markdown(yaml_file, markdown_file)
