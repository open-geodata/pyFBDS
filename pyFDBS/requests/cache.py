"""
Para cache das requisições
"""

from datetime import timedelta

import requests
import requests_cache

# Configuração do cache
requests_cache.install_cache(
    cache_name="fbds_cache",  # Nome do arquivo de cache
    backend="sqlite",  # Backend para armazenamento (SQLite)
    expire_after=timedelta(days=3),  # Cache expira após X dias
    allowable_methods=("GET", "POST"),  # Métodos HTTP permitidos
)


def make_request(url):
    """
    Faz uma requisição HTTP com suporte a cache

    Parameters:
    -----------
    url : str
        URL para fazer a requisição

    Returns:
    --------
    response : requests.Response
        Resposta da requisição
    is_cached : bool
        Indica se a resposta veio do cache
    """
    response = requests.get(url)
    is_cached = getattr(response, "from_cache", False)

    # Informação sobre o cache
    # cache_status = 'CACHE' if is_cached else 'NOVA REQUISIÇÃO'
    # print(f"{cache_status}: {url}")

    return response, is_cached
