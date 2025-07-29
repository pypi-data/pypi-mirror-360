from setuptools import setup, find_packages
import pathlib

# Para pegar o README como descrição longa (importante para PyPI)
HERE = pathlib.Path(__file__).parent
long_description = (HERE / "README.md").read_text(encoding="utf-8")

setup(
    name="selenium-gourmet",  # Use traço ou underline, mas mantenha consistente
    version="0.2.2",           # Use versão semântica (sem ".")
    packages=find_packages(include=["selenium_gourmet", "selenium_gourmet.*", "gourmet"]),
    install_requires=[
        "click>=8.1.7",
        "selenium>=4.10.0",
        # Adicione outras libs que seu projeto depende
    ],
    entry_points={
        "console_scripts": [
            "gourmet=selenium_gourmet.cli.main:cli",
        ],
    },
    author="Natã Assis",
    author_email="srassis2014@gmail.com",  # bom ter contato
    description="Gerador de projetos Selenium com estrutura gourmet",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/natan33/selenium-gourmet",  # link do repo
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # ou outra licença
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
