import os

def update_readme():
    blueprint_dir = 'automations'
    readme_file = os.path.join(blueprint_dir, 'README.md')
    blueprints = []

    # Traverse the directory and gather blueprint directories containing README.md
    for root, dirs, files in os.walk(blueprint_dir):
        # Skip 'dev' folder
        dirs[:] = [d for d in dirs if d != 'dev']

        for dir_name in dirs:
            readme_path = os.path.join(root, dir_name, 'README.md')
            if os.path.isfile(readme_path):
                blueprint_path = os.path.relpath(readme_path, blueprint_dir)
                blueprint_name = dir_name
                blueprints.append((blueprint_name, blueprint_path))

    # Read the current README.md file
    with open(readme_file, 'r') as file:
        readme_lines = file.readlines()

    # Find the start and end indices of the Available Blueprints section
    start_index = readme_lines.index('## Available Blueprints\n') + 1
    end_index = start_index
    while end_index < len(readme_lines) and (readme_lines[end_index].startswith('-') or readme_lines[end_index].strip() == ''):
        end_index += 1

    # Generate the new content for the Available Blueprints section
    blueprint_lines = ['\n']
    for name, path in blueprints:
        blueprint_lines.append(f'- [{name}](./{path})\n')

    # Replace the old Available Blueprints section with the new content
    new_readme_lines = readme_lines[:start_index] + blueprint_lines + ['\n'] + readme_lines[end_index:]

    # Write the updated content back to the README.md file
    with open(readme_file, 'w') as file:
        file.writelines(new_readme_lines)

if __name__ == "__main__":
    update_readme()
