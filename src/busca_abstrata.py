from dataclasses import dataclass
from heapq import heappop, heappush
from itertools import count
from math import inf

from src.astar import heuristica_octil
from src.grafo_abstrato import (
    ArestaAbstrata,
    GrafoAbstrato,
    NoAbstrato,
)


@dataclass(slots=True)
class ResultadoBuscaAbstrata:
    """
    Resultado da busca realizada no grafo abstrato.
    """

    encontrado: bool
    nos: list[NoAbstrato]
    arestas: list[ArestaAbstrata]
    custo: float
    nos_expandidos: int


def reconstruir_rota_abstrata(
    anteriores: dict[
        NoAbstrato,
        tuple[NoAbstrato, ArestaAbstrata],
    ],
    inicio: NoAbstrato,
    destino: NoAbstrato,
) -> tuple[list[NoAbstrato], list[ArestaAbstrata]]:
    """
    Reconstrói a sequência de nós e arestas
    escolhida pela busca.
    """

    nos = [destino]
    arestas = []

    no_atual = destino

    while no_atual != inicio:
        no_anterior, aresta_utilizada = anteriores[no_atual]

        arestas.append(aresta_utilizada)
        no_atual = no_anterior
        nos.append(no_atual)

    nos.reverse()
    arestas.reverse()

    return nos, arestas


def buscar_no_grafo_abstrato(
    grafo: GrafoAbstrato,
    inicio: NoAbstrato,
    destino: NoAbstrato,
) -> ResultadoBuscaAbstrata:
    """
    Executa uma busca A* sobre o grafo abstrato.
    """

    if inicio not in grafo.adjacencias:
        return ResultadoBuscaAbstrata(
            encontrado=False,
            nos=[],
            arestas=[],
            custo=inf,
            nos_expandidos=0,
        )

    if destino not in grafo.adjacencias:
        return ResultadoBuscaAbstrata(
            encontrado=False,
            nos=[],
            arestas=[],
            custo=inf,
            nos_expandidos=0,
        )

    fila_prioridade = []
    contador = count()

    custos: dict[NoAbstrato, float] = {
        inicio: 0.0
    }

    anteriores: dict[
        NoAbstrato,
        tuple[NoAbstrato, ArestaAbstrata],
    ] = {}

    visitados: set[NoAbstrato] = set()

    heappush(
        fila_prioridade,
        (
            heuristica_octil(
                inicio.posicao,
                destino.posicao,
            ),
            next(contador),
            inicio,
        ),
    )

    nos_expandidos = 0

    while fila_prioridade:
        _, _, no_atual = heappop(
            fila_prioridade
        )

        if no_atual in visitados:
            continue

        visitados.add(no_atual)
        nos_expandidos += 1

        if no_atual == destino:
            nos, arestas = reconstruir_rota_abstrata(
                anteriores=anteriores,
                inicio=inicio,
                destino=destino,
            )

            return ResultadoBuscaAbstrata(
                encontrado=True,
                nos=nos,
                arestas=arestas,
                custo=custos[destino],
                nos_expandidos=nos_expandidos,
            )

        for aresta in grafo.vizinhos(no_atual):
            vizinho = aresta.destino

            novo_custo = (
                custos[no_atual]
                + aresta.custo
            )

            custo_anterior = custos.get(
                vizinho,
                inf,
            )

            if novo_custo < custo_anterior:
                custos[vizinho] = novo_custo

                anteriores[vizinho] = (
                    no_atual,
                    aresta,
                )

                prioridade = (
                    novo_custo
                    + heuristica_octil(
                        vizinho.posicao,
                        destino.posicao,
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

    return ResultadoBuscaAbstrata(
        encontrado=False,
        nos=[],
        arestas=[],
        custo=inf,
        nos_expandidos=nos_expandidos,
    )


def montar_caminho_do_grid(
    arestas: list[ArestaAbstrata],
) -> list[tuple[int, int]]:
    """
    Junta os pequenos caminhos armazenados nas
    arestas abstratas em um único caminho no grid.
    """

    if not arestas:
        return []

    caminho_completo = list(
        arestas[0].caminho
    )

    for aresta in arestas[1:]:
        trecho = list(aresta.caminho)

        if (
            caminho_completo
            and trecho
            and caminho_completo[-1] == trecho[0]
        ):
            trecho = trecho[1:]

        caminho_completo.extend(trecho)

    return caminho_completo