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
        f.write(f"# {data['blueprint'].get('name', 'Unnamed Blueprint')}\n\n")
        f.write(f"## Description\n{data['blueprint'].get('description', 'No description')}\n\n")
        f.write(f"## Source\n[{data['blueprint'].get('source_url', 'No source URL')}]({data['blueprint'].get('source_url', 'No source URL')})\n\n")
        f.write(f"## Domain\n{data['blueprint'].get('domain', 'No domain')}\n\n")
        f.write(f"## Home Assistant Minimum Version\n{data['blueprint'].get('homeassistant', {}).get('min_version', 'No version specified')}\n\n")
        
        f.write(f"## Inputs\n\n")
        
        for section in ['required_entities', 'optional_entities']:
            if section in data['blueprint']['input']:
                f.write(f"### {data['blueprint']['input'][section].get('name', 'Unnamed Section')}\n")
                f.write(f"{data['blueprint']['input'][section].get('description', 'No description')}\n\n")
                for key, value in data['blueprint']['input'][section]['input'].items():
                    f.write(f"- **{value.get('name', 'Unnamed Input')}**\n")
                    f.write(f"  - **Description**: {value.get('description', 'No description')}\n")
                    if 'default' in value:
                        f.write(f"  - **Default**: {value['default']}\n")
                    if 'selector' in value:
                        f.write(f"  - **Selector**: `{value['selector']}`\n")
                    f.write("\n")

        f.write("## Variables\n")
        for key, value in data.get('variables', {}).items():
            f.write(f"- `{key}`: {value}\n")

        f.write("\n## Triggers\n")
        for trigger in data.get('trigger', []):
            trigger_id = trigger.get('id', 'Unknown')
            platform = trigger.get('platform', 'Unknown')
            from_state = trigger.get('from', 'Unknown')
            to_state = trigger.get('to', 'Unknown')
            f.write(f"- **{trigger_id}**: Triggered when the {platform} changes from `{from_state}` to `{to_state}`.\n")

        f.write("\n## Conditions\n")
        for condition in data.get('condition', []):
            f.write(f"- **{condition.get('condition', 'Unknown Condition')}**: {condition.get('value_template', 'No value template')}\n")

        f.write("\n## Actions\n")
        for action in data.get('action', []):
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
                if 'service' in action:
                    service = action.get('service', 'Unknown service')
                    data = action.get('data', 'No data')
                    f.write(f"- **{service}**: {data}\n")
                if 'delay' in action:
                    delay = action.get('delay', 'No delay specified')
                    f.write(f"- **Delay**: {delay}\n")
                if 'wait_template' in action:
                    wait_template = action.get('wait_template', 'No wait template specified')
                    f.write(f"- **Wait Template**: {wait_template}\n")

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
