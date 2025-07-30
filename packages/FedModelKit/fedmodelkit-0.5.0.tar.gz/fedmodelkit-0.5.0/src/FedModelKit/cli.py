import os
import sys
import argparse
from .templates import (
    get_main_template,
    get_task_template,
    get_readme_template,
    get_server_template,
    get_client_template,
    get_pyproject_template,
    get_extern_pyproject_template,
    get_uv_template,
    get_init_template,
    get_ds_template,
    get_images,
)

def create_structure(exp_name: str = "new_experiment") -> None:
    root_dir = os.getcwd()

    structure = {
        f"{exp_name}": {
            "main.py": get_main_template(),
            "pyproject.toml": get_pyproject_template(exp_name),
            f"{exp_name}": {
                "__init__.py": get_init_template(),
                "task.py": get_task_template(),
                "server_app.py": get_server_template(),
                "client_app.py": get_client_template(),                
            },
        },
        "pyproject.toml": get_extern_pyproject_template(exp_name),
        "uv.lock": get_uv_template(),
        "README.md": get_readme_template(),
        "ds.ipynb": get_ds_template(),
    }


    for name, content in structure.items():
        path = os.path.join(root_dir, name)
        if isinstance(content, dict):  # If content is a folder
            os.makedirs(path, exist_ok=True)
            for name1, content1 in content.items():
                nested_path = os.path.join(path, name1)
                if isinstance(content1, dict):  # If nested content is a folder
                    os.makedirs(nested_path, exist_ok=True)
                    for name2, content2 in content1.items():
                        nested_nested_path = os.path.join(nested_path, name2)
                        with open(nested_nested_path, "w") as f:
                            f.write(content2)
                else:
                    with open(nested_path, "w") as f:
                        f.write(content1)
        else:  # Single file at the root
            with open(path, "w") as f:
                f.write(content)
    # Create images directory and copy images
    get_images(root_dir)

    print(f"Project structure for {exp_name} created successfully in {root_dir}.")


'''def main():
    if len(sys.argv) < 2:
        print("Usage: msi <command> [options]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "init":
        structure_type = sys.argv[2] if len(sys.argv) > 2 else "default"
        create_structure(structure_type)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
'''

def main():
    if len(sys.argv) < 2:
        print("Usage: fmk init -n/--name [project_name]")
        sys.exit(1)
    
    parser = argparse.ArgumentParser(prog='fmk', description='FedModelKit CLI for managing federated learning projects')
    subparsers = parser.add_subparsers(dest='command')


    # init subcommand
    init_parser = subparsers.add_parser('init', help='Initialize the project')
    init_parser.add_argument('-n', '--name', required=True, help='Set the experiment title')

    args = parser.parse_args()

    if args.command == 'init':
        print(f"Initializing project with title: {args.name}")
        
        # Create the project structure
        create_structure(args.name)
