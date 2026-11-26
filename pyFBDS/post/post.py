"""
Módulo com classe que uso o LXML massivamente
"""

import tarfile
import tempfile
from datetime import timedelta
from pathlib import Path
from typing import Literal
from urllib.parse import urlencode
import requests
import geopandas as gpd
from time import monotonic
import requests_cache
from more_itertools import one

from ..logger import FBDSLogger
from ..lxml import FBDS as FBDS_web


class FBDS:
    def __init__(
        self,
        output_path: Path | str,
        temp_path: Path | str | None = None,
        logger: FBDSLogger | None = None,
    ) -> None:
        self.temp_path = Path(temp_path or tempfile.gettempdir())
        self.temp_path.mkdir(exist_ok=True, parents=True)
        self.output_path = Path(output_path)
        self.output_path.mkdir(exist_ok=True, parents=True)
        self.url_base = "https://geo.fbds.org.br/"
        self.logger = logger or FBDSLogger()

        # Configuração do cache
        self.session = requests_cache.CachedSession(
            cache_name=str(self.temp_path / "fbds_cache"),  # Nome do arquivo de cache
            backend="sqlite",  # Backend para armazenamento (SQLite)
            expire_after=timedelta(days=3),  # Cache expira após X dias
            allowable_methods=("GET", "POST"),  # Métodos HTTP permitidos
        )

    def prepare_payload(self, uf, municipality) -> dict[str, str]:
        self.logger.logger.info(f"Preparando payload para {municipality}/{uf}")
        fdbs = FBDS_web(
            temp_path=self.temp_path,
            output_path=self.output_path,
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

    def download(
        self,
        municipality: str,
        uf: str,
        max_download_seconds: float = 600,
    ) -> Path:
        """
        Faz o download dos dados do município

        :param uf: Sigla do Estado
        :type uf: str
        :param municipality: Nome do Município
        :type municipality: str
        :return: Caminho do arquivo salvo
        :rtype: Path
        """
        # ddd
        self.logger.logger.info("Preparando payload do download")
        dados = self.prepare_payload(
            uf=uf,
            municipality=municipality,
        )
        self.logger.logger.info("Payload preparado; iniciando download")

        if max_download_seconds <= 0:
            raise ValueError("max_download_seconds deve ser maior que zero")

        filepath = self.output_path / dados["as"]
        partial_path = filepath.with_suffix(filepath.suffix + ".part")
        deadline = monotonic() + max_download_seconds

        # ...existing code...
        try:
            self.logger.logger.info("Enviando POST; aguardando resposta do servidor")
            with self.session.cache_disabled():
                with self.session.post(
                    url="https://geo.fbds.org.br/",
                    data=urlencode(dados),
                    headers={
                        "User-Agent": "Mozilla/5.0",
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                    timeout=(10, 15),
                    stream=True,
                ) as r:
                    self.logger.logger.info(
                        "Resposta recebida: status=%s, content-length=%s",
                        r.status_code,
                        r.headers.get("Content-Length", "desconhecido"),
                    )
                    r.raise_for_status()

                    received = 0
                    with partial_path.open("wb") as file:
                        for chunk in r.iter_content(chunk_size=1024 * 1024):
                            if monotonic() >= deadline:
                                raise requests.exceptions.Timeout(
                                    "O tempo máximo de download foi excedido."
                                )
                            if chunk:
                                file.write(chunk)
                                received += len(chunk)
                                self.logger.logger.info(
                                    "Download recebido: %.1f MB",
                                    received / (1024 * 1024),
                                )

            if monotonic() >= deadline:
                raise requests.exceptions.Timeout(
                    "O tempo máximo de download foi excedido."
                )

            partial_path.replace(filepath)
        # ...existing code...

        except requests.exceptions.Timeout:
            partial_path.unlink(missing_ok=True)
            self.logger.logger.error("O tempo máximo de download foi excedido.")
            raise
        except requests.exceptions.RequestException:
            partial_path.unlink(missing_ok=True)
            self.logger.logger.exception("Falha na requisição do download.")
            raise

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

        list_shps = [Path(x).stem for x in list_shps]
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
            values = "\n".join(list_shps_clean)
            raise RuntimeError(
                f"Para o município '{municipality}' é preciso que o layer esteja entre\n{values}"
            )

        # Seleciona shapefile
        arquivo = one(x for x in list_shps if x.endswith(f"{layer}.shp"))
        print(arquivo)

        # Cria geodataframe
        # O GDAL/Fiona usa o prefixo /vsitar/ para abrir arquivos tar/tar.gz
        return gpd.read_file(filename=f"/vsitar/{filepath}/{arquivo}")
