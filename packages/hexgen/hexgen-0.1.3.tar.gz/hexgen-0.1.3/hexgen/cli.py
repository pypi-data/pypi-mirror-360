import os
import shutil
import click

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")

# Estrutura de pastas com dtos fora de clients
FOLDERS = [
    "src/application/routers",
    "src/application/use_cases",
    "src/domain/entities",
    "src/domain/interfaces",
    "src/domain/services",
    "src/config",
    "src/infra/repositories",
    "src/infra/clients",
    "src/infra/dtos",
    "tests",
    ".github/workflows"
]

TEMPLATE_MAP = {
    "README.md": "README.md",
    "requirements.txt": "requirements.txt",
    ".gitignore": ".gitignore",
    "serverless.yaml": "serverless.yaml",
    "main.py": "src/main.py",
    "custom_config.py": "src/config/custom_config.py",
    "dependency_start.py": "src/config/dependency_start.py",
    "aws_deploy.yml": ".github/workflows/aws_deploy.yml",
}


def add_init_files_recursively(folder_path: str):
    """Adiciona __init__.py em todas as pastas recursivamente"""
    for root, dirs, _ in os.walk(folder_path):
        for dir in dirs:
            init_path = os.path.join(root, dir, "__init__.py")
            os.makedirs(os.path.dirname(init_path), exist_ok=True)
            if not os.path.exists(init_path):
                with open(init_path, "w") as f:
                    f.write("")


@click.command()
@click.argument("project_name")
def generate(project_name: str):
    """Gera uma estrutura de projeto com arquitetura hexagonal usando templates"""
    os.makedirs(project_name, exist_ok=True)

    # Cria as pastas
    for folder in FOLDERS:
        path = os.path.join(project_name, folder)
        os.makedirs(path, exist_ok=True)

    # Adiciona __init__.py em todas as subpastas de src/
    src_path = os.path.join(project_name, "src")
    add_init_files_recursively(src_path)

    # Copia os arquivos de template para seus destinos
    for template_file, target_relative_path in TEMPLATE_MAP.items():
        source_path = os.path.join(TEMPLATE_DIR, template_file)
        target_path = os.path.join(project_name, target_relative_path)

        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        shutil.copyfile(source_path, target_path)

    click.secho(f"✅ Projeto '{project_name}' gerado com sucesso usando templates!", fg="green")


def main():
    generate.main(standalone_mode=True)
