import os
import textwrap

def generate_project(name, example):
    print(f"📦 Gerando projeto: {name}")
    structure = ["tests", "pages", "data", "utils","controller"]
    os.makedirs(name, exist_ok=True)
    for folder in structure:
        os.makedirs(os.path.join(name, folder), exist_ok=True)

    main_py_code = textwrap.dedent("""
        from core import create_main

        main = create_main()

        if __name__ == "__main__":
            main()
    """)
    with open(os.path.join(name, "main.py"), "w") as f:
        f.write(main_py_code)

    conteudo_page_google_ = textwrap.dedent("""
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from utils.elements import GoogleElements

    class GooglePage:
        def __init__(self, driver):
            self.driver = driver
            self.url = GoogleElements.GOOGLE_URL
            self.search_input = (By.NAME, GoogleElements.SEARCH_INPUT[1])

        def open(self):
            self.driver.get(self.url)

        def search(self, query):
            search_box = self.driver.find_element(*self.search_box_locator)
            search_box.clear()
            search_box.send_keys(query)
            search_box.send_keys(Keys.RETURN)

    """)

    core_folder_page = os.path.join(name, "pages")
    os.makedirs(core_folder_page, exist_ok=True)

    with open(os.path.join(core_folder_page, "page_google.py"), "w") as f:
        f.write(conteudo_page_google_)


    core_folder_elements = os.path.join(name, "utils")
    os.makedirs(core_folder_elements, exist_ok=True) 

    elements_page_google_ = textwrap.dedent("""
    from selenium.webdriver.common.by import By

    class GoogleElements:
        SEARCH_BOX = (By.NAME, "q")

        GOOGLE_URL = "https://www.google.com"

    """)

    with open(os.path.join(core_folder_elements, "elements_google.py"), "w") as f:
        f.write(elements_page_google_)


    controller_folder = os.path.join(name, "controller")
    google_controller_code = textwrap.dedent("""
        from pages.page_google import GooglePage

        def buscar_no_google(driver, termo):
            pagina = GooglePage(driver)
            pagina.search(termo)
    """)
    with open(os.path.join(controller_folder, "google_controller.py"), "w") as f:
        f.write(google_controller_code)

    core_folder = os.path.join(name, "core")
    os.makedirs(core_folder, exist_ok=True)

    driver_code = textwrap.dedent("""
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from selenium_stealth import stealth
        from webdriver_manager.chrome import ChromeDriverManager

        def initialize_driver(headless=False):
            options = Options()
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("start-maximized")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)
            options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                 "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
            options.add_experimental_option("prefs", {
                "profile.default_content_setting_values.notifications": 2
            })
            if headless:
                options.add_argument("--headless=new")
                options.add_argument("--disable-gpu")
                options.add_argument("--window-size=1920,1080")
                options.add_argument("--disable-software-rasterizer")
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': 'Object.defineProperty(navigator, "webdriver", { get: () => undefined })'
            })
            stealth(driver,
                    languages=["en-US", "en"],
                    vendor="Google Inc.",
                    platform="Win32",
                    webgl_vendor="Intel Inc.",
                    renderer="Intel Iris OpenGL",
                    fix_hairline=True)
            return driver
    """)
    with open(os.path.join(core_folder, "driver.py"), "w") as f:
        f.write(driver_code)

    __init__code = textwrap.dedent("""
        from core.driver import initialize_driver
        from time import sleep

        def create_main():
            def main():
                driver = initialize_driver()
                buscar_no_google(driver, "Python Selenium")
                sleep(3)
                driver.quit()
            return main
    """)

    with open(os.path.join(core_folder, "__init__.py"), "w") as f:
        f.write(__init__code)


    config_code = textwrap.dedent("""
        from dotenv import load_dotenv
        import os

        load_dotenv()  # Carrega o .env na raiz do projeto

        USER = os.getenv("USER")
        PASSWORD = os.getenv("PASSWORD")
    """)

    with open(os.path.join(core_folder, "config.py"), "w") as f:
        f.write(config_code)

    with open(os.path.join(name, "requirements.txt"), "w") as f:
        f.write("pytest\nbeautifulsoup4\npandas\nnumpy\nselenium-stealth\nwebdriver-manager\n")
        f.write("selenium\n")

    with open(os.path.join(name, ".gitignore"), "w") as f:
        f.write("__pycache__/\n.venv/\n.env\n")

    with open(os.path.join(name, "README.md"), "w", encoding="utf-8") as f:
        f.write(textwrap.dedent("""
        # {name}

        Gerador de projetos Selenium ou SeleniumBase com qualidade gourmet 🍷

        ## 📁 Estrutura do Projeto

        {name} /
        │
        ├── core/ # Configuração de driver e serviços
        ├── pages/ # Page Objects (interação com elementos)
        ├── controller/ # Regras de negócio e orquestrações
        ├── utils/ # Utilitários e configurações
        ├── data/ # Dados de entrada / saída
        ├── tests/ # Testes automatizados
        ├── main.py # Ponto de entrada (apenas executa)
        ├── .env # Variáveis de ambiente
        ├── requirements.txt # Dependências do projeto
        └── README.md # Este tutorial


        ## 🧪 Como executar os testes com `pytest`
        Dentro da pasta do projeto gerado, execute:


        > pytest

        4. Exemplos de uso do pytest
        Executar com mais detalhes (modo verboso):
        ```bash
        > pytest -v
        ```

        Rodar apenas um teste específico (ex: test_example.py):

        ```bash
        pytest -k "example"
        ```
        Mostrar navegador (apenas com seleniumbase):

        ```bash
        pytest --headed
        ```
        ### 1. Instale as dependências
        ```bash
        > pip install -r requirements.txt
        ```
    """))

    with open(os.path.join(name, ".env"), "w") as f:
        f.write("USER=seu_usuario\nPASSWORD=sua_senha\n")

    with open(os.path.join(name, "Dockerfile"), "w") as f:
        f.write(textwrap.dedent("""
            FROM python:3.12-slim
            WORKDIR /app
            COPY . .
            RUN pip install --upgrade pip && \\
                pip install -r requirements.txt
            CMD ["pytest", "--headed", "--maxfail=1"]
        """))

    if example:
        with open(os.path.join(name, "tests", "test_example.py"), "w") as f:
            f.write("def test_exemplo():\n    assert True\n")

    print("✅ Projeto criado com sucesso!")
