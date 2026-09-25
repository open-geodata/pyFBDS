import io
import tempfile
import unicodedata
from datetime import timedelta
from pathlib import Path

import pandas as pd
import requests_cache
from more_itertools import one

from ..compare import ComparadorTexto
from ..lxml.web import FBDS


class IBGE:
    def __init__(
        self,
        fbds: FBDS,
        temp_path: Path | str,
    ) -> None:
        self.fbds = fbds
        self.temp_path = temp_path
        self.logger = fbds.logger

        # Cria pasta temporária
        if self.temp_path is None:
            self.temp_path = tempfile.gettempdir()
        self.temp_path = Path(temp_path)
        self.temp_path.mkdir(exist_ok=True, parents=True)

        self.temp_path.mkdir(exist_ok=True, parents=True)
        # self.output_path.mkdir(exist_ok=True, parents=True)

        # Configuração do cache
        self.session = requests_cache.CachedSession(
            cache_name=str(self.temp_path / "fbds_cache"),  # Nome do arquivo de cache
            backend="sqlite",  # Backend para armazenamento (SQLite)
            expire_after=timedelta(days=3),  # Cache expira após X dias
            allowable_methods=("GET", "POST"),  # Métodos HTTP permitidos
        )

        # Lê tabela
        self.data = self.read_dataframe()

    @property
    def url_xls(self) -> str:
        """
        Obter URL da pasta

        :return: _description_
        :rtype: _type_
        """
        list_files = self.fbds.get_files()
        dados_xls = one([x for x in list_files if x["name"].endswith(".xls")])
        return dados_xls["url"]

    def read_dataframe(self) -> pd.DataFrame:
        """
        Lê, com cache, tabela que contem o nome e IDs dos municípios

        :return: Tabela obtida no FDBS
        :rtype: pd.DataFrame
        """
        # Faz o download usando a sessão COM CACHE
        response = self.session.get(self.url_xls)

        # Garante que não houve erro HTTP (ex: 404)
        response.raise_for_status()

        # Passa os bytes do conteúdo para o read_excel via BytesIO
        df = pd.read_excel(
            io.BytesIO(response.content),
            skiprows=1,
            usecols=["GEOCODIGO", "Município", "UF"],
        )

        # Removendo apenas as linhas inteiramente nulas
        df = df.dropna(how="all")

        # Convertendo a coluna 'idade' para int
        df["GEOCODIGO"] = df["GEOCODIGO"].astype(int)

        # Renomeando as colunas
        df = df.rename(
            columns={
                "GEOCODIGO": "geocodigo",
                "Município": "municipio",
                "UF": "uf",
            }
        )
        return df

    def search(self, id_ibge: int = 3548500) -> tuple[str, str]:
        """
        _summary_

        :param id_ibge: _description_, defaults to 3548500
        :type id_ibge: int, optional
        :raises RuntimeError: _description_
        :return: _description_
        :rtype: tuple[str, str]
        """

        self.logger.logger.info(f"Procura código do IBGE {id_ibge}")

        # Busca a linha onde o geocodigo é igual ao código desejado
        mask = self.data["geocodigo"] == id_ibge
        resultado = self.data.loc[mask, ["municipio", "uf"]]

        if not resultado.empty:
            municipio = resultado.iloc[0]["municipio"]
            uf = resultado.iloc[0]["uf"]

            self.logger.logger.info(
                f"Encontrei o município {municipio} - {uf} na tabela do Excel."
            )

            # Trata Municípios
            municipio = self.trata_municipio(municipio=municipio)
            self.logger.logger.info(
                f"Reduzir para buscar coincidir como nome da pasta. Passei para {municipio}"
            )

            # Busca nome por tolerência
            municipio, uf = self.search_municipio(
                municipality=municipio,
                uf=uf,
                tolerancia=0.94,
            )
            return municipio, uf

        else:
            raise RuntimeError("Código não encontrado.")

    def trata_municipio(self, municipio: str) -> str:

        if not isinstance(municipio, str):
            raise TypeError("Precisa ser texto")

        # Normaliza em NFD (separa a letra do acento)
        nfkd = unicodedata.normalize("NFD", municipio)

        # Filtra mantendo apenas o que não for acento/marca gráfica (Mn)
        municipio = "".join([c for c in nfkd if unicodedata.category(c) != "Mn"])
        municipio = municipio.replace(" ", "_")
        municipio = municipio.replace("'", "")
        municipio = municipio.upper()
        return municipio

    def search_municipio(self, municipality: str, uf: str, tolerancia=0.94):
        # ddd
        municipios_uf = self.fbds.municipios(uf=uf)

        # Compara texto
        comparador = ComparadorTexto(limite_minimo=0.2)

        top_x = comparador.buscar_top_x_semelhantes(
            alvo=municipality,
            opcoes=municipios_uf,
            top_x=5,
        )

        # Busca o primeiro nome cujo score seja igual a 1
        municipio = next((nome for nome, score in top_x if score == 1), None)

        # Lista de municípios maior que tolerância
        municipios = [nome for nome, score in top_x if score > 0.94]

        # dddd
        if municipio:
            self.logger.logger.info(
                "Município encontrado. Bateu 100%. Avança pra download."
            )

        # Filtrando um único item com tolerância > 0.94. Aceito!
        elif len(municipios) == 1:
            municipality = municipios[0]
            self.logger.logger.info(
                f"Município {municipality} encontrado com intervalo de tolerancia de {tolerancia}. Avança pra download."
            )

        # Mais de um com 0.94. Putz., Necessário definir.
        elif len(municipios) >= 2:
            desc = "\n".join([f"{x} -> Similaridade de {y}" for x, y in top_x])
            raise RuntimeError(
                f"Com a tolerância de {tolerancia} existe mais de um registro. Necessário especificar.\n{desc}"
            )

        else:
            raise RuntimeError("Erro genérico. Como entrei aqui!?")

        return municipality, uf

    # def search_uf(self, id_ibge: int = 3548500):

    #     UFS_IBGE = {
    #         11: "RO",
    #         12: "AC",
    #         13: "AM",
    #         14: "RR",
    #         15: "PA",
    #         16: "AP",
    #         17: "TO",
    #         21: "MA",
    #         22: "PI",
    #         23: "CE",
    #         24: "RN",
    #         25: "PB",
    #         26: "PE",
    #         27: "AL",
    #         28: "SE",
    #         29: "BA",
    #         31: "MG",
    #         32: "ES",
    #         33: "RJ",
    #         35: "SP",
    #         41: "PR",
    #         42: "SC",
    #         43: "RS",
    #         50: "MS",
    #         51: "MT",
    #         52: "GO",
    #         53: "DF",
    #     }
    #     # Extrai os 2 primeiros dígitos
    #     codigo_uf = int(str(id_ibge)[:2])
    #     estado = UFS_IBGE.get(codigo_uf, "UF não encontrada")
    #     print(estado)  # Saída: 'SP'
    #     return estado
