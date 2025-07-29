import os
import click
from selenium_gourmet.core.generator import generate_project
from selenium_gourmet.core.installer import install_dependencies

@click.command()
@click.option("--name", required=True, help="Nome do projeto")
@click.option("--install", is_flag=True, help="Instalar as dependências automaticamente")
def cli(name, install):
    """Selenium Gourmet CLI - cria projeto e instala dependências"""
    generate_project(name, example=True)

    if install:
        project_path = os.path.abspath(name)
        install_dependencies(project_path)

if __name__ == "__main__":
    cli()
