"""
Módulo para comparar texto
"""

from difflib import SequenceMatcher
from typing import List, Tuple, Optional


class ComparadorTexto:
    """Classe utilitária para comparação e busca de similaridade entre textos."""

    def __init__(self, limite_minimo: float = 0.0):
        """
        :param limite_minimo: Nota mínima de similaridade (de 0.0 a 1.0) para incluir no resultado.
        """
        self.limite_minimo = limite_minimo

    def calcular_similaridade(self, texto1: str, texto2: str) -> float:
        """Calcula o percentual de similaridade entre duas strings (0.0 a 1.0)."""
        return SequenceMatcher(None, texto1, texto2).ratio()

    def buscar_top_x_semelhantes(
        self, alvo: str, opcoes: List[str], top_x: int = 3
    ) -> List[Tuple[str, float]]:
        """
        Retorna os X itens mais semelhantes ordenados da maior para a menor similaridade.

        :param alvo: A string que você quer buscar.
        :param opcoes: Lista de strings para comparar.
        :param top_x: Quantidade de primeiros resultados a retornar.
        :return: Lista de tuplas com [(item, pontuacao), ...]
        """
        if not opcoes:
            return []

        # Calcula a similaridade para todos os itens
        resultados = [
            (opcao, self.calcular_similaridade(alvo, opcao)) for opcao in opcoes
        ]

        # Filtra pelo limite mínimo estipulado
        resultados_filtrados = [
            res for res in resultados if res[1] >= self.limite_minimo
        ]

        # Ordena do maior percentual para o menor
        resultados_ordenados = sorted(
            resultados_filtrados, key=lambda x: x[1], reverse=True
        )

        # Retorna apenas os X primeiros
        return resultados_ordenados[:top_x]


if __name__ == "__main__":
    comparador = ComparadorTexto(limite_minimo=0.2)

    alvo = "Maçã"
    opcoes = ["Maca", "Massa", "Banana", "Melancia", "Abacaxi", "Maracujá"]

    # Retorna os 3 mais semelhantes
    top_3 = comparador.buscar_top_x_semelhantes(alvo, opcoes, top_x=3)
    print([x for x, y in top_3])

    print(f"Top resultados para '{alvo}':")
    for posicao, (item, pontuacao) in enumerate(top_3, start=1):
        print(f"{posicao}º: {item} ({pontuacao * 100:.2f}%)")
