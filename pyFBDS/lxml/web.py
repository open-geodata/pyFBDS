"""
Módulo com classe que uso o LXML massivamente
"""

import asyncio
import tempfile
from datetime import timedelta
from pathlib import Path
from urllib.parse import urljoin

import aiohttp
import requests_cache
from lxml import html
from tqdm.asyncio import tqdm_asyncio

from ..compare import ComparadorTexto
from ..logger import FBDSLogger


class FBDS:
    def __init__(
        self,
        output_path: Path | str,
        temp_path: Path | str | None = None,
        logger: FBDSLogger | None = None,
    ) -> None:
        self.output_path.mkdir(exist_ok=True, parents=True)
        self.temp_path = Path(temp_path or tempfile.gettempdir())
        self.temp_path.mkdir(exist_ok=True, parents=True)
        self.output_path = Path(output_path)
        self.url_base = "https://geo.fbds.org.br/"
        self.logger = logger or FBDSLogger()

        # Configuração do cache
        self.session = requests_cache.CachedSession(
            cache_name=str(self.temp_path / "fbds_cache"),  # Nome do arquivo de cache
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
        list_states = self.get_links(url=self.url_base, ignore_first=1)

        # Só pega as pastas que tem só suas letras (SP, RJ, PA, AC)
        list_states = [x for x in list_states if len(x["name"]) == 2]
        return list_states

    def get_files(self) -> list[dict]:
        """
        Retorna lista contendo dicionários com informações sobre arquivos na raiz do geoportal,
        de acordo com o que está disponível no [FBDS](https://geo.fbds.org.br/).

        :return: Lista contendo dicionários com informações sobre arquivos.
        :rtype: list
        """
        self.logger.logger.info("Obtendo estados")
        list_states = self.get_links(url=self.url_base, ignore_first=1)

        # Só pega as pastas que tem só suas letras (SP, RJ, PA, AC)
        list_states = [x for x in list_states if len(x["name"]) != 2]
        return list_states

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
        municipios_uf = self.municipios(uf=uf)
        top_x = comparador.buscar_top_x_semelhantes(
            alvo=municipality,
            opcoes=municipios_uf,
            top_x=5,
        )

        # Confere se foi definido um municicipio válido
        if municipality not in municipios_uf:
            desc = "\n".join([f"{x} -> Similaridade de {y}" for x, y in top_x])
            raise RuntimeError(
                f"Precisa ser municipio válido\nTalvez algum destes:\n{desc}"
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

    async def download_file_async(
        self,
        session,
        url_info,
    ):
        """
        Download assíncrono de um único arquivo

        Parameters:
        -----------
        session : aiohttp.ClientSession
            Sessão HTTP assíncrona
        url_info : dict
            Dicionário com informações do arquivo (url, name, etc)
        output_dir : str or Path
            Diretório onde salvar o arquivo
        """
        try:
            url = url_info["url"]
            # Remove o base URL e usa o caminho relativo
            relative_path = url.replace("https://geo.fbds.org.br/", "")
            output_path = Path(self.output_path) / relative_path

            # Cria o diretório se não existir
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Faz o download
            async with session.get(url) as response:
                if response.status == 200:
                    content = await response.read()

                    # Salva o arquivo
                    with open(file=output_path, mode="wb") as f:
                        f.write(content)

                    result = {
                        "nome": url_info["name"],
                        "status": "sucesso",
                        "size": len(content),
                    }
                else:
                    result = {
                        "nome": url_info["name"],
                        "status": "erro",
                        "erro": f"Status code: {response.status}",
                    }
        except Exception as e:
            result = {"nome": url_info["name"], "status": "erro", "erro": str(e)}

        return result

    async def download_files_async(
        self,
        url_list,
        max_concurrent=5,
    ):
        """
        Download assíncrono de múltiplos arquivos

        Parameters:
        -----------
        url_list : list
            Lista de dicionários com informações dos arquivos
        output_dir : str or Path
            Diretório onde salvar os arquivos
        max_concurrent : int
            Número máximo de downloads simultâneos
        """
        # Configura conexão com limite de conexões simultâneas
        conn = aiohttp.TCPConnector(limit=max_concurrent)

        async with aiohttp.ClientSession(connector=conn) as session:
            # Cria a lista de tarefas
            tasks = []
            for url_info in url_list:
                task = self.download_file_async(session, url_info)
                tasks.append(task)

            # Executa as tasks com barra de progresso
            results = await tqdm_asyncio.gather(
                *tasks,
                desc="Downloading files",
                total=len(tasks),
                ascii=True,  # Melhor compatibilidade
                mininterval=0.5,  # Atualiza a cada 0.5 segundos
            )

        return results

    def download_files_parallel(
        self,
        url_list: list,
        max_concurrent=5,
        logger=None,
    ):
        """
        Wrapper para executar o download assíncrono

        :param url_list: Lista de dicionários com informações dos arquivos
        :type url_list: list
        :param output_dir: Diretório onde salvar os arquivos
        :type output_dir: str or Path
        :param max_concurrent: Número máximo de downloads simultâneos
        :type max_concurrent: int, optional
        :param logger: Logger existente para usar. Se None, cria um novo.
        :type logger: FBDSLogger, optional
        :return: _description_
        :rtype: _type_
        """

        try:
            # Usa o logger fornecido ou cria um novo
            # if logger is None:
            #     logger = FBDSLogger()
            self.logger.start_download_session()

            # Pega o loop de eventos atual ou cria um novo se não existir
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            # Se estamos em um notebook IPython, use o nest_asyncio
            try:
                import nest_asyncio

                nest_asyncio.apply()
            except ImportError:
                pass

            # Executa o download assíncrono
            results = loop.run_until_complete(
                self.download_files_async(
                    url_list=url_list,
                    max_concurrent=max_concurrent,
                )
            )

            # Analisa e registra os resultados
            self.logger.analyze_results(results)
            return results

        except Exception as e:
            self.logger.logger.error(f"Erro durante o download: {e!s}")
            return []
