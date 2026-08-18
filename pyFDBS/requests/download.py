"""
Módulo para download dos dados usando asyncio
"""

import asyncio
from pathlib import Path

import aiohttp
from tqdm.asyncio import tqdm_asyncio

from .logger import FBDSLogger

#from tqdm.notebook import tqdm

#from .cache import make_request


async def download_file_async(session, url_info, output_dir):
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
        output_path = Path(output_dir) / relative_path

        # Cria o diretório se não existir
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Faz o download
        async with session.get(url) as response:
            if response.status == 200:
                content = await response.read()

                # Salva o arquivo
                with open(output_path, "wb") as f:
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


async def download_files_async(url_list, output_dir, max_concurrent=5):
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
            task = download_file_async(session, url_info, output_dir)
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


def download_files_parallel(url_list, output_dir, max_concurrent=5, logger=None):
    """
    Wrapper para executar o download assíncrono

    Parameters:
    -----------
    url_list : list
        Lista de dicionários com informações dos arquivos
    output_dir : str or Path
        Diretório onde salvar os arquivos
    max_concurrent : int
        Número máximo de downloads simultâneos
    logger : FBDSLogger, optional
        Logger existente para usar. Se None, cria um novo.
    """
    try:
        # Usa o logger fornecido ou cria um novo
        if logger is None:
            logger = FBDSLogger()
        logger.start_download_session()

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
            download_files_async(url_list, output_dir, max_concurrent)
        )

        # Analisa e registra os resultados
        logger.analyze_results(results)
        return results

    except Exception as e:
        logger.logger.error(f"Erro durante o download: {str(e)}")
        return []
