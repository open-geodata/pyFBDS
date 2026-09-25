"""
Módulo para usar driver do Chrome
"""

import tempfile
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions

from . import config


class Chrome(webdriver.Chrome):
    """
    Cria driver customizado do Selenium

    :param webdriver: _description_
    :type webdriver: _type_
    """

    def __init__(
        self,
        # driver_path: Path,
        # logs_path: Path,
        # down_path: Path,
        *args,
        **kwargs,
    ):
        """
        - verify_ssl
        - headless
        - download_path
        """
        # Parameters
        headless = kwargs.get("headless", False)
        self.download_path = kwargs.get("download_path", False)
        modo_colab = kwargs.get("modo_colab", False)

        # Temp Path
        temp_path = tempfile.gettempdir()
        project_temp_path = Path(temp_path) / config.TEMP_PATH_NAME

        # Scrapy Path
        scrapy_path = project_temp_path / "scrapy"
        scrapy_path.mkdir(exist_ok=True, parents=True)

        # Download Path
        if self.download_path is False:
            # Cria Pasta
            self.download_path = scrapy_path / "download"
            self.download_path.mkdir(exist_ok=True, parents=True)

        # my_service = ChromeService()
        # print(str(self.download_path))
        # print(self.download_path)
        # print(self.download_path.is_dir())
        # print(str(self.download_path) + os.path.sep)

        # Options
        options = ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-gpu")

        # Se tem Modo Anônimo, o download não funciona adequadamente
        # options.add_argument('--incognito')

        # Certificados
        options.add_argument("--ignore-certificate-errors-spki-list")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--ignore-ssl-errors")

        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")
        # options.add_argument('--disable-logging')
        # Remove a mensagem "Chrome is being controlled by automated test software"
        # que aparece quando o Chrome é iniciado pelo Selenium.
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        # Desativa a extensão de automação do Chrome que é carregada por
        # padrão quando o Chrome é iniciado pelo Selenium.
        # Isso ajuda a evitar que sites detectem que o navegador está
        # sendo controlado por um script de automação.
        options.add_experimental_option("useAutomationExtension", False)

        options.add_experimental_option(
            "prefs",
            {
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False,
                "download.default_directory": str(self.download_path),
                # + os.path.sep,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True,
            },
        )

        if headless is True:
            options.add_argument("--headless")

        if modo_colab is True:
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")

        super().__init__(
            # service=my_service,
            options=options
        )
        self.maximize_window()
