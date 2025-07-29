import os
import subprocess
import sys
from pathlib import Path

def install_dependencies(project_dir):
    project_path = Path(project_dir)
    venv_path = project_path / "venv"
    python_exec = venv_path / "Scripts" / "python.exe"

    print("📦 Criando ambiente virtual...")
    subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)

    pip_exec = venv_path / "Scripts" / "pip.exe" if os.name == "nt" else venv_path / "bin" / "pip"


    print("⬆️ Atualizando pip...")
    subprocess.run([str(python_exec), "-m", "pip", "install", "--upgrade", "pip"], check=True)

    print("📦 Instalando dependências do requirements.txt...")
    subprocess.run([str(pip_exec), "install", "-r", str(project_path / "requirements.txt")], check=True)

    print("✅ Ambiente virtual criado e pacotes instalados.")
    print(f"💡 Para ativar o ambiente virtual:")
    if os.name == "nt":
        print(fr"    {project_dir}/venv/bin/activate")
    else:
        print(fr"    source {project_dir}/venv/bin/activate")


