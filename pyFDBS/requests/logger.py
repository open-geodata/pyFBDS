"""
Sistema de logs para a aplicação FBDS
"""

import json
import logging
from datetime import datetime
from pathlib import Path

# Obtém o diretório raiz do projeto
PROJECT_ROOT = Path(__file__).parent.parent
DEFAULT_LOG_DIR = PROJECT_ROOT / "logs"


class FBDSLogger:
    _instance = None
    _initialized = False

    def __new__(cls, log_dir=None, new_session=False):
        # Verifica se já existe uma instância ou se foi pedida uma nova sessão
        if cls._instance is None or new_session:
            # Cria uma nova instância se não existir ou se new_session=True
            cls._instance = super(FBDSLogger, cls).__new__(cls)
            # Marca como não inicializado para forçar a execução do __init__
            cls._initialized = False
        # Retorna a instância (seja ela nova ou existente)
        return cls._instance

    def __init__(self, log_dir=None, new_session=False):
        if not self._initialized or new_session:
            # Usa o diretório fornecido ou o padrão
            self.log_dir = Path(log_dir) if log_dir else DEFAULT_LOG_DIR
            self.log_dir.mkdir(parents=True, exist_ok=True)

            # Configura o logger principal
            self.logger = logging.getLogger("FBDS")
            self.logger.setLevel(logging.INFO)

            # Remove handlers anteriores se existirem
            for handler in self.logger.handlers[:]:
                self.logger.removeHandler(handler)

            # Cria handlers
            self._setup_handlers()

            # Dicionário para armazenar estatísticas
            self.stats = {
                "total": 0,
                "success": 0,
                "errors": 0,
                "cached": 0,
                "start_time": None,
                "end_time": None,
                "errors_list": [],
            }

            self._initialized = True

    def _setup_handlers(self):
        # Handler para arquivo
        # Usa apenas a data, não o timestamp completo
        date_str = datetime.now().strftime("%Y%m%d")
        self.log_file = self.log_dir / f"fbds_{date_str}.log"
        # self.stats_file = self.log_dir / f'stats_{date_str}.json'

        file_handler = logging.FileHandler(self.log_file, encoding="utf-8", mode="a")
        file_handler.setLevel(logging.INFO)

        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Formato do log
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Adiciona handlers ao logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def start_download_session(self):
        """Inicia uma nova sessão de download"""
        self.stats = {
            "total": 0,
            "success": 0,
            "errors": 0,
            "cached": 0,
            "start_time": datetime.now(),
            "end_time": None,
            "errors_list": [],
        }
        self.logger.info("Iniciando nova sessão de download")

    def end_download_session(self):
        """Finaliza a sessão de download e gera relatório"""
        self.stats["end_time"] = datetime.now()
        duration = self.stats["end_time"] - self.stats["start_time"]

        # Log do resumo
        self.logger.info(f"=== Resumo da Sessão de Download ===")
        self.logger.info(
            f"Downloads com sucesso: {self.stats['success']} de {self.stats['total']}"
        )
        if self.stats["errors"] > 0:
            self.logger.error(f"Erros: {self.stats['errors']} de {self.stats['total']}")
        # self.logger.info(
        #     f"Arquivos do cache: {self.stats['cached']} de {self.stats['total']}"
        # )
        self.logger.info(f"Duração total: {duration}")

        # Se houver erros, registra eles
        if self.stats["errors_list"]:
            self.logger.error("Erros encontrados:")
            for error in self.stats["errors_list"]:
                self.logger.error(f"- {error['nome']}: {error['erro']}")

        # # Salva as estatísticas em JSON
        # stats_file = (
        #     self.log_dir
        #     / f'stats_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        # )
        # with open(stats_file, 'w', encoding='utf-8') as f:
        #     # Converte datetime para string
        #     stats_dict = self.stats.copy()
        #     stats_dict['start_time'] = self.stats['start_time'].isoformat()
        #     stats_dict['end_time'] = self.stats['end_time'].isoformat()
        #     json.dump(stats_dict, f, ensure_ascii=False, indent=4)

    def log_result(self, result):
        """Registra o resultado de um download"""
        self.stats["total"] += 1

        if result.get("cached", False):
            self.stats["cached"] += 1
            self.logger.info(f"Arquivo em cache: {result['nome']}")

        if result["status"] == "sucesso":
            self.stats["success"] += 1
            self.logger.info(
                f"Download concluído: {result['nome']} ({result['size']} bytes)"
            )
        else:
            self.stats["errors"] += 1
            self.stats["errors_list"].append(result)
            self.logger.error(f"Erro no download de {result['nome']}: {result['erro']}")

    def analyze_results(self, results):
        """
        Analisa os resultados dos downloads
        """
        self.start_download_session()

        for result in results:
            self.log_result(result)

        self.end_download_session()
        return self.stats
