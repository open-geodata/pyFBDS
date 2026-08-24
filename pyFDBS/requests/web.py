"""
Módulo com classe que uso o LXML massivamente
"""

import tempfile
from datetime import timedelta
from pathlib import Path
from urllib.parse import urljoin

import requests_cache
from lxml import html


class FBDS:
    def __init__(self, temp_path: Path | str) -> None:
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

    def get_links(self, url, ignore_first):
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
        # response, is_cached = make_request(url=url)
        r = self.session.get(url=url)

        origem = "Cache" if r.from_cache else "WEB"
        print(f"[{origem}]")

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
                print("Entrei aqui!?")
                pass

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
        :return: _description_
        :rtype: list[dict]
        """
        return self.get_links(url=self.url_base, ignore_first=1)

    def get_municipalities(self, uf):
        state = self.get_state(uf=uf)
        url = state["url"]
        return self.get_links(url=url, ignore_first=2)

    def get_layers(self, municipality, uf):
        municipalitie = self.get_municipalitie(municipality=municipality, uf=uf)
        url = municipalitie["url"]
        return self.get_links(url=url, ignore_first=2)

    def get_state(self, uf=None):
        states = self.get_states()
        return next(x for x in states if x["name"] == uf)

    def get_municipalitie(self, municipality=None, uf=None):
        municipalities = self.get_municipalities(uf=uf)
        return next(x for x in municipalities if x["name"] == municipality)

    def get_layer(self, municipality=None, uf=None, layer=None):
        layers = self.get_layers(municipality=municipality, uf=uf)
        return next(x for x in layers if x["name"] == layer)
