import os
import shutil
from pathlib import Path
from importlib import resources

def get_task_template():
    current_dir = os.path.dirname(__file__)
    template_path = os.path.join(current_dir, os.path.join("templates", 'task_template.py'))
    with open(template_path, 'r') as file:
        return file.read()


def get_main_template():
    current_dir = os.path.dirname(__file__)
    template_path = os.path.join(current_dir, os.path.join("templates", 'main_template.py'))
    with open(template_path, 'r') as file:
        return file.read()


def get_readme_template() -> str:
    current_dir = os.path.dirname(__file__)
    template_path = os.path.join(current_dir, os.path.join("templates", 'readme_template.md'))
    with open(template_path, 'r') as file:
        return file.read()
    

def get_server_template() -> str:
    current_dir = os.path.dirname(__file__)
    template_path = os.path.join(current_dir, os.path.join("templates", 'server_app_template.py'))
    with open(template_path, 'r') as file:
        return file.read()
    
def get_client_template() -> str:  
    current_dir = os.path.dirname(__file__)
    template_path = os.path.join(current_dir, os.path.join("templates", 'client_app_template.py'))
    with open(template_path, 'r') as file:
        return file.read()
    
def get_pyproject_template(experiment_name: str) -> str:
    current_dir = os.path.dirname(__file__)
    template_path = os.path.join(current_dir, os.path.join("templates", 'pyproject_template.toml'))
    with open(template_path, 'r') as file:
        return file.read().replace("EXPERIMENT_NAME", experiment_name)
    

def get_extern_pyproject_template(experiment_name: str) -> str:
    current_dir = os.path.dirname(__file__)
    template_path = os.path.join(current_dir, os.path.join("templates", 'extern_pyproject_template.toml'))
    with open(template_path, 'r') as file:
        return file.read().replace("EXPERIMENT_NAME", experiment_name)

def get_uv_template() -> str:
    current_dir = os.path.dirname(__file__)
    template_path = os.path.join(current_dir, os.path.join("templates", 'uv_template.lock'))
    with open(template_path, 'r') as file:
        return file.read()

def get_init_template() -> str:
    current_dir = os.path.dirname(__file__)
    template_path = os.path.join(current_dir, os.path.join("templates", '__init__template.py'))
    with open(template_path, 'r') as file:
        return file.read()
    
def get_ds_template() -> str:
    current_dir = os.path.dirname(__file__)
    template_path = os.path.join(current_dir, os.path.join("templates", 'ds_template.ipynb'))
    with open(template_path, 'r') as file:
        return file.read()
    
def get_images(output_folder) -> None:
    current_dir = os.path.dirname(__file__)
    img_path = Path(current_dir) / 'templates' / 'images'
    target = Path(output_folder) / 'images'
    target.mkdir(parents=True, exist_ok=True)
    for image in img_path.iterdir():
        shutil.copy(image, target / image.name)