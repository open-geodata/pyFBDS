"""
Módulo com classe que uso o LXML massivamente
"""

from pathlib import Path
from urllib.parse import urljoin

from lxml import html

from .cache import make_request


class FBDS:
    def __init__(self) -> None:
        self.url_base = "https://geo.fbds.org.br/"

    def get_links(self, url, ignore_first):
        # Usa a função make_request com cache
        response, is_cached = make_request(url)
        response.raise_for_status()
        tree = html.fromstring(response.content)

        list_folders = []
        folders = tree.xpath("//tr")

        # Ignora o primeiro tr, que é o cabeçalho
        folders = folders[ignore_first:]

        for folder in folders:
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
        return [x for x in states if x["name"] == uf][0]

    def get_municipalitie(self, municipality=None, uf=None):
        municipalities = self.get_municipalities(uf=uf)
        return [x for x in municipalities if x["name"] == municipality][0]

    def get_layer(self, municipality=None, uf=None, layer=None):
        layers = self.get_layers(municipality=municipality, uf=uf)
        return [x for x in layers if x["name"] == layer][0]
