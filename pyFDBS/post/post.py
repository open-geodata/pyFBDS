"""
Módulo com classe que uso o LXML massivamente
"""

import pprint
import tarfile
import tempfile
from datetime import timedelta
from pathlib import Path
from urllib.parse import urlencode

import requests_cache

from ..requests.web import FBDS as FBDS_Web


class FBDS:
    def __init__(self, temp_path: Path | str) -> None:
        self.temp_path = temp_path
        self.url_base = "https://geo.fbds.org.br/"

        # Cria pasta temporária
        if temp_path is None:
            temp_path = tempfile.gettempdir()
        temp_path = Path(temp_path)
        temp_path.mkdir(exist_ok=True, parents=True)

        # Configuração do cache
        self.session = requests_cache.CachedSession(
            cache_name=str(temp_path / "fbds_cache"),  # Nome do arquivo de cache
            backend="sqlite",  # Backend para armazenamento (SQLite)
            expire_after=timedelta(days=3),  # Cache expira após X dias
            allowable_methods=("GET", "POST"),  # Métodos HTTP permitidos
        )

    def prepare_payload(self, uf, municipality):
        fdbs = FBDS_Web(temp_path=self.temp_path)
        municipio = fdbs.get_municipalitie(
            uf=uf,
            municipality=municipality,
        )

        return {
            "action": "download",
            "as": f"{municipality}.tar",
            "type": "php-tar",
            "baseHref": f"/{uf}/",
            "hrefs": "",
            "hrefs[0]": f"/{municipio['url'].removeprefix(self.url_base)}",
        }

    def download(self, uf, municipality, output_path):
        dados = self.prepare_payload(
            uf=uf,
            municipality=municipality,
        )

        r = self.session.post(
            # Qualquer um dos 3 prefixos de url servem
            # url="https://geo.fbds.org.br/SP/?",
            # url="https://geo.fbds.org.br/SP/",
            url="https://geo.fbds.org.br/",
            data=urlencode(dados),
            # Precisa ter o parâmetro headers
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )

        filename = dados["as"]
        print(f'O arquivo terá o nome de "{filename}"')

        # Salva Arquivo
        filepath = output_path / filename
        with open(file=filepath, mode="wb") as f:
            f.write(r.content)
        return filepath

    def list_shapefiles(self, filepath):
        # Printa Lista de Arquivos
        with tarfile.open(name=filepath, mode="r") as tar_ref:
            # Listar todos os arquivos que terminam com .shp (ignorando maiúsculas/minúsculas)
            arquivos_shp = [
                nome for nome in tar_ref.getnames() if nome.lower().endswith(".shp")
            ]

        pprint.pprint(arquivos_shp)
        return arquivos_shp
