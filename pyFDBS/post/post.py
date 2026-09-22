"""
Módulo com classe que uso o LXML massivamente
"""

import tarfile
import tempfile
from datetime import timedelta
from pathlib import Path
from typing import Literal
from urllib.parse import urlencode

import geopandas as gpd
import requests_cache
from more_itertools import one

from ..logger import FBDSLogger
from ..lxml import FBDS as FBDS_web


class FBDS:
    def __init__(
        self,
        temp_path: Path | str,
        output_path: Path | str,
        logger: FBDSLogger | None = None,
    ) -> None:
        self.temp_path = temp_path
        self.output_path = output_path
        self.url_base = "https://geo.fbds.org.br/"
        self.logger = logger or FBDSLogger()

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
        self.logger.logger.info(f"Preparando payload para {municipality}/{uf}")
        fdbs = FBDS_web(
            temp_path=self.temp_path,
            logger=self.logger,
        )

        # dddd
        municipio = fdbs.get_municipalitie(
            uf=uf,
            municipality=municipality,
        )

        # ddd
        return {
            "action": "download",
            "as": f"{municipality}.tar",
            "type": "php-tar",
            "baseHref": f"/{uf}/",
            "hrefs": "",
            "hrefs[0]": f"/{municipio['url'].removeprefix(self.url_base)}",
        }

    def download(self, uf, municipality) -> Path:
        """
        _summary_

        :param uf: _description_
        :type uf: _type_
        :param municipality: _description_
        :type municipality: _type_
        :return: _description_
        :rtype: Path
        """
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

        r.raise_for_status()

        filename = dados["as"]
        self.logger.logger.info(f'O arquivo terá o nome de "{filename}"')

        # Salva Arquivo
        filepath = Path(self.output_path) / filename
        with open(file=filepath, mode="wb") as f:
            f.write(r.content)

        # Logs
        self.logger.logger.info(f"Arquivo salvo em {filepath}")
        return filepath

    def list_shapefiles(self, filepath: str | Path) -> list[str]:
        """
        Retorna a lista dos arquivos *shapefile* disponíveis no arquivo `.tar`.

        :param filepath: Caminho do arquivo .tar obtido com a função `download`.
        :type filepath: str | Path
        :return: List de Arquivos shapefile
        :rtype: list[str]
        """
        # Printa Lista de Arquivos
        with tarfile.open(name=filepath, mode="r") as tar_ref:
            # Listar todos os arquivos que terminam com .shp (ignorando maiúsculas/minúsculas)
            list_shps = [
                nome for nome in tar_ref.getnames() if nome.lower().endswith(".shp")
            ]

        self.logger.logger.info(
            f"Arquivos shapefile encontrados em {filepath}: {list_shps}"
        )
        return list_shps

    def clean_list(self, filepath: str | Path) -> list[str]:
        list_shps = self.list_shapefiles(filepath=filepath)
        list_shps = [x.split("_", maxsplit=2)[2] for x in list_shps]
        list_shps = [x.replace(".shp", "") for x in list_shps]
        list_shps = list(set(list_shps))
        list_shps.sort()
        return list_shps

    def read_data(
        self,
        uf,
        municipality,
        layer: Literal[
            "APP",
            "APP_USO",
            "MASSAS_DAGUA",
            "MASSA_DAGUA",
            "MASSA_DAGUAS",
            "NASCENTE",
            "NASCENTES",
            "RIOS_DUPLOS",
            "RIOS_DUPLOS_",
            "RIOS_DUPLOS_POL",
            "RIOS_SIMPLES",
            "USO",
        ] = "MASSAS_DAGUA",
    ) -> gpd.GeoDataFrame:

        # Faz o download do arquivo
        filepath = self.download(
            uf=uf,
            municipality=municipality,
        )

        # Lista os shapefiles disponíveis
        list_shps = self.list_shapefiles(filepath=filepath)

        # Lista de Layers Disponíveis
        list_shps_clean = self.clean_list(filepath=filepath)
        if layer not in list_shps_clean:
            raise RuntimeError(
                f"Para o município '{municipality}' é preciso que o layer esteja entre\n{'\n'.join(list_shps_clean)}"
            )

        # Seleciona shapefile
        arquivo = one(x for x in list_shps if x.endswith(f"{layer}.shp"))
        print(arquivo)

        # Cria geodataframe
        # O GDAL/Fiona usa o prefixo /vsitar/ para abrir arquivos tar/tar.gz
        return gpd.read_file(filename=f"/vsitar/{filepath}/{arquivo}")
