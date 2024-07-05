import os

def update_readme():
    blueprint_dir = 'automation'
    readme_file = os.path.join(blueprint_dir, 'README.md')
    blueprints = []

    # Traverse the directory and gather blueprint directories containing README.md
    for root, dirs, files in os.walk(blueprint_dir):
        # Skip 'dev' folder
        dirs[:] = [d for d in dirs if d != 'dev']

        for file in files:
            if file == 'README.md':
                blueprint_path = os.path.relpath(os.path.join(root, file), blueprint_dir)
                blueprint_name = os.path.basename(os.path.dirname(blueprint_path))
                blueprints.append((blueprint_name, blueprint_path))

    # Read the current README.md file
    with open(readme_file, 'r') as file:
        readme_lines = file.readlines()

    # Find the index where the Available Blueprints section starts
    start_index = readme_lines.index('## Available Blueprints\n') + 1

    # Find the index where the Available Blueprints section ends
    end_index = start_index
    while end_index < len(readme_lines) and readme_lines[end_index].startswith('-'):
        end_index += 1

    # Generate the new content for the Available Blueprints section
    blueprint_lines = ['\n']
    for name, path in blueprints:
        blueprint_lines.append(f'- [{name}](./{path})\n')

    # Replace the old Available Blueprints section with the new content
    new_readme_lines = readme_lines[:start_index] + blueprint_lines + readme_lines[end_index:]

    # Write the updated content back to the README.md file
    with open(readme_file, 'w') as file:
        file.writelines(new_readme_lines)

if __name__ == "__main__":
    update_readme()
