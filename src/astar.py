from dataclasses import dataclass
from heapq import heappop, heappush
from itertools import count
from math import inf, sqrt
from time import perf_counter

from src.grid import Grid, Posicao


@dataclass
class ResultadoBusca:
    encontrado: bool
    caminho: list[Posicao]
    custo: float
    nos_expandidos: int
    tempo_segundos: float


def heuristica_octil(
    posicao_atual: Posicao,
    destino: Posicao,
) -> float:
    """
    Estima a distância restante considerando movimentos
    retos e diagonais.
    """

    diferenca_linhas = abs(posicao_atual[0] - destino[0])
    diferenca_colunas = abs(posicao_atual[1] - destino[1])

    menor_diferenca = min(
        diferenca_linhas,
        diferenca_colunas,
    )

    maior_diferenca = max(
        diferenca_linhas,
        diferenca_colunas,
    )

    return (
        maior_diferenca
        + (sqrt(2) - 1) * menor_diferenca
    )


def reconstruir_caminho(
    anteriores: dict[Posicao, Posicao],
    destino: Posicao,
) -> list[Posicao]:
    caminho = [destino]
    posicao_atual = destino

    while posicao_atual in anteriores:
        posicao_atual = anteriores[posicao_atual]
        caminho.append(posicao_atual)

    caminho.reverse()

    return caminho


def buscar_caminho(
    grid: Grid,
    inicio: Posicao,
    destino: Posicao,
) -> ResultadoBusca:
    """
    Executa o algoritmo A* entre o início e o destino.
    """

    if not grid.esta_livre(inicio):
        raise ValueError(
            "A posição inicial está fora do mapa "
            "ou contém um obstáculo."
        )

    if not grid.esta_livre(destino):
        raise ValueError(
            "A posição de destino está fora do mapa "
            "ou contém um obstáculo."
        )

    tempo_inicial = perf_counter()

    fila_prioridade = []
    contador = count()

    prioridade_inicial = heuristica_octil(
        inicio,
        destino,
    )

    heappush(
        fila_prioridade,
        (
            prioridade_inicial,
            next(contador),
            inicio,
        ),
    )

    anteriores: dict[Posicao, Posicao] = {}

    custos: dict[Posicao, float] = {
        inicio: 0.0
    }

    visitados: set[Posicao] = set()

    nos_expandidos = 0

    while fila_prioridade:
        _, _, posicao_atual = heappop(
            fila_prioridade
        )

        if posicao_atual in visitados:
            continue

        visitados.add(posicao_atual)
        nos_expandidos += 1

        if posicao_atual == destino:
            tempo_total = (
                perf_counter() - tempo_inicial
            )

            caminho = reconstruir_caminho(
                anteriores,
                destino,
            )

            return ResultadoBusca(
                encontrado=True,
                caminho=caminho,
                custo=custos[destino],
                nos_expandidos=nos_expandidos,
                tempo_segundos=tempo_total,
            )

        for vizinho, custo_movimento in grid.vizinhos(
            posicao_atual
        ):
            novo_custo = (
                custos[posicao_atual]
                + custo_movimento
            )

            custo_anterior = custos.get(
                vizinho,
                inf,
            )

            if novo_custo < custo_anterior:
                custos[vizinho] = novo_custo
                anteriores[vizinho] = posicao_atual

                prioridade = (
                    novo_custo
                    + heuristica_octil(
                        vizinho,
                        destino,
                    )
                )

                heappush(
                    fila_prioridade,
                    (
                        prioridade,
                        next(contador),
                        vizinho,
                    ),
                )

    tempo_total = perf_counter() - tempo_inicial

    return ResultadoBusca(
        encontrado=False,
        caminho=[],
        custo=inf,
        nos_expandidos=nos_expandidos,
        tempo_segundos=tempo_total,
    )