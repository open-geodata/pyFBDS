"""
Módulo com classe que uso o LXML massivamente
"""

import tempfile
from datetime import timedelta
from pathlib import Path
from urllib.parse import urljoin

import requests_cache
from lxml import html

from ..compare import ComparadorTexto
from ..logger import FBDSLogger


class FBDS:
    def __init__(
        self,
        temp_path: Path | str,
        logger: FBDSLogger | None = None,
    ) -> None:
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

    def close(self) -> None:
        """Fecha a sessão HTTP e libera as conexões mantidas em pool."""
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def get_links(self, url, ignore_first) -> list:
        """
        Obtém todos os links de uma página e opcionalmente os tamanhos das pastas

        Parameters:
        -----------
        url : str
            URL da página
        get_size : bool
            Se True, tenta obter o tamanho das pastas
        """
        # Usa a função make_request com cache
        r = self.session.get(url=url)

        # ddd
        origem = "Cache" if r.from_cache else "WEB"
        self.logger.logger.info(f"[{origem}] {url}")

        # dddd
        r.raise_for_status()

        tree = html.fromstring(html=r.content)

        # Links a ignorar
        ignore_links = [
            "http://browsehappy.com",
            "https://larsjung.de/h5ai/",
        ]

        list_folders = []
        folders = tree.xpath("//tr")

        # Ignora o primeiro tr, que é o cabeçalho
        folders = folders[ignore_first:]

        for folder in folders:
            link = folder.xpath(".//a/@href")[0]
            if any(ignore in link for ignore in ignore_links):
                self.logger.logger.error("Entrei aqui!?")

            # Get Data
            link = folder.xpath('.//td[@class="fb-n"]/a/@href')[0]
            tipo = folder.xpath('.//td[@class="fb-i"]/img/@src')[0]
            name = folder.xpath('.//td[@class="fb-n"]/a')[0].text.strip()
            data = folder.xpath('.//td[@class="fb-d"]')[0].text.strip()
            size = folder.xpath('.//td[@class="fb-s"]')[0].text.strip()

            # Append to list
            list_folders.append(
                {
                    "url": urljoin(self.url_base, link),
                    "type": Path(tipo).stem,
                    "name": name,
                    "date": data,
                    "size": size,
                }
            )
        return list_folders

    def get_states(self) -> list[dict]:
        """
        Retorna lista contendo dicionários com informações sobre os estados,
        de acordo com o que está disponível no [FBDS](https://geo.fbds.org.br/).

        :return: Lista contendo dicionários com informações sobre as Unidades da Federação (UFs).
        :rtype: list
        """
        self.logger.logger.info("Obtendo estados")
        return self.get_links(url=self.url_base, ignore_first=1)

    def get_state(self, uf):
        """
        Retorna um dicionário contendo informações sobre uma Unidade da Federação específica.

        :param uf: Sigla da Unidade da Federação (UF). Por exemplo: "SP", "RJ", "PE"
        :type uf: str
        :return: Dicionário contendo informações sobre uma Unidade da Federação específica.
        :rtype: dict
        """

        # Passa para maiúscula
        uf = uf.upper()

        # Confere se foi definido um estado válido
        if uf not in self.states:
            raise RuntimeError(f"Precisa ser estado válido\n{', '.join(self.states)}")

        states = self.get_states()
        return next(x for x in states if x["name"] == uf)

    @property
    def states(self) -> list[str]:
        """
        Retorna a lista das Unidades da Federação (UF),
        de acordo com o que está disponível no [FBDS](https://geo.fbds.org.br/).
        """
        return [x["name"] for x in self.get_states() if len(x["name"]) == 2]

    def municipios(self, uf: str) -> list[str]:
        """
        Lista os Municípios de um Estado

        :param uf: Sigla da Unidade da Federação (UF). Por exemplo: "SP", "RJ", "PE"
        :type uf: str
        :return: Lista os Municípios de um Estado
        :rtype: list[dict]
        """
        # Passa para maiúscula
        uf = uf.upper()

        return [x["name"] for x in self.get_municipalities(uf=uf)]

    def get_municipalities(self, uf: str) -> list[dict]:
        """
        Retorna lista contendo dicionários com informações sobre os municípios,
        de acordo com o que está disponível no [FBDS](https://geo.fbds.org.br/).

        :param uf: Sigla da Unidade da Federação (UF). Por exemplo: "SP", "RJ", "PE"
        :type uf: str
        :return: Lista contendo dicionários com informações sobre os municípios.
        :rtype: list[dict]
        """

        # Confere se foi definido um estado válido
        if uf not in self.states:
            raise RuntimeError(f"Precisa ser estado válido\n{', '.join(self.states)}")

        state = self.get_state(uf=uf)
        url = state["url"]
        return self.get_links(url=url, ignore_first=2)

    def get_municipalitie(self, municipality: str, uf: str):
        """
        _summary_

        :param municipality: _description_
        :type municipality: _type_
        :param uf: Sigla da Unidade da Federação (UF). Por exemplo: "SP", "RJ", "PE"
        :type uf: str
        :return: _description_
        :rtype: dict
        """

        # Confere que é string
        if not isinstance(municipality, str):
            raise TypeError("Precisa ser string")

        # Compara texto
        comparador = ComparadorTexto(limite_minimo=0.2)

        # Retorna os X mais semelhantes
        top_x = comparador.buscar_top_x_semelhantes(
            alvo=municipality,
            opcoes=self.municipios(uf=uf),
            top_x=5,
        )

        # Confere se foi definido um municicipio válido
        if municipality not in self.municipios(uf=uf):
            raise RuntimeError(
                f"Precisa ser municipio válido\nTalvez algum destes:\n{'\n'.join([x for x, _ in top_x])}"
            )

        municipalities = self.get_municipalities(uf=uf)
        return next(x for x in municipalities if x["name"] == municipality)

    def get_layers(self, municipality, uf) -> list:
        """
        Retorna a lista de *layers* de um dado município,
        de acordo com o que está disponível no [FBDS](https://geo.fbds.org.br/).

        :param municipality: Nome do Município de acordo com o que consta no FBDS
        :type municipality: str
        :param uf: Sigla da Unidade da Federação (UF). Por exemplo: "SP", "RJ", "PE"
        :type uf: str
        :return: Lista de *layers* de um dado município
        :rtype: list
        """

        municipalitie = self.get_municipalitie(
            municipality=municipality,
            uf=uf,
        )
        url = municipalitie["url"]
        return self.get_links(url=url, ignore_first=2)

    def get_layer(self, municipality: str, uf: str, layer: str):
        """
        _summary_

        :param municipality: Nome do Município de acordo com o que consta no FBDS
        :type municipality: str
        :param uf: Sigla da Unidade da Federação (UF). Por exemplo: "SP", "RJ", "PE"
        :type uf: str
        :param layer: _description_, defaults to None
        :type layer: _type_, optional
        :return: _description_
        :rtype: _type_
        """

        layers = self.get_layers(municipality=municipality, uf=uf)
        return next(x for x in layers if x["name"] == layer)
