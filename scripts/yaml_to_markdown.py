import yaml
import sys
import os

# Define a custom constructor to handle unknown tags
def construct_ignore(loader, node):
    return None

# Register the custom constructor for the '!input' tag
yaml.add_constructor('!input', construct_ignore, Loader=yaml.SafeLoader)

def yaml_to_markdown(yaml_file, markdown_file):
    with open(yaml_file, 'r') as f:
        data = yaml.safe_load(f)
    
    if 'blueprint' not in data:
        print(f"Skipping {yaml_file}: 'blueprint' key not found.")
        return

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
            trigger_id = trigger.get('id', 'Unknown')
            platform = trigger.get('platform', 'Unknown')
            from_state = trigger.get('from', 'Unknown')
            to_state = trigger.get('to', 'Unknown')
            f.write(f"- **{trigger_id}**: Triggered when the {platform} changes from `{from_state}` to `{to_state}`.\n")

        f.write("\n## Actions\n")
        for action in data['action']:
            if 'choose' in action:
                for choice in action['choose']:
                    conditions = choice.get('conditions', [])
                    if conditions:
                        condition_id = conditions[0].get('id', 'Unknown')
                        f.write(f"### {condition_id}\n")
                    for step in choice.get('sequence', []):
                        service = step.get('service', 'Unknown service')
                        data = step.get('data', 'No data')
                        f.write(f"- **{service}**: {data}\n")
            else:
                # Handle other types of actions if necessary
                pass

        # Make mode optional
        mode = data.get('mode', 'Not specified')
        f.write(f"\n## Mode\n")
        f.write(f"- **Mode**: {mode}\n")

        # Handle max_exceeded if present
        max_exceeded = data.get('max_exceeded', 'Not specified')
        f.write(f"- **Max Exceeded**: {max_exceeded}\n")

if __name__ == "__main__":
    yaml_file = sys.argv[1]
    output_dir = os.path.dirname(yaml_file)
    markdown_file = os.path.join(output_dir, 'README.md')
    yaml_to_markdown(yaml_file, markdown_file)
