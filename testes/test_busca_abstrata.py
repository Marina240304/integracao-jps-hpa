from math import isclose, sqrt

from src.busca_abstrata import (
    buscar_no_grafo_abstrato,
    montar_caminho_do_grid,
)
from src.grafo_abstrato import (
    NoAbstrato,
    construir_grafo_abstrato,
)
from src.grid import Grid
from src.hpa import (
    dividir_em_clusters,
    identificar_portais,
)


def criar_grafo_abstrato_de_teste():
    matriz = [
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
    ]

    grid = Grid.criar(matriz)

    clusters = dividir_em_clusters(
        grid=grid,
        tamanho_cluster=3,
    )

    portais = identificar_portais(
        grid=grid,
        clusters=clusters,
    )

    grafo = construir_grafo_abstrato(
        grid=grid,
        clusters=clusters,
        portais=portais,
    )

    return grafo


def test_busca_encontra_rota_no_grafo_abstrato() -> None:
    grafo = criar_grafo_abstrato_de_teste()

    inicio = NoAbstrato(
        cluster_id=0,
        posicao=(1, 2),
    )

    destino = NoAbstrato(
        cluster_id=3,
        posicao=(4, 3),
    )

    resultado = buscar_no_grafo_abstrato(
        grafo=grafo,
        inicio=inicio,
        destino=destino,
    )

    assert resultado.encontrado is True
    assert resultado.nos[0] == inicio
    assert resultado.nos[-1] == destino

    assert isclose(
        resultado.custo,
        2.0 + 2.0 * sqrt(2),
    )

    caminho_grid = montar_caminho_do_grid(
        resultado.arestas
    )

    assert caminho_grid[0] == inicio.posicao
    assert caminho_grid[-1] == destino.posicao


def test_busca_falha_para_no_inexistente() -> None:
    grafo = criar_grafo_abstrato_de_teste()

    inicio = NoAbstrato(
        cluster_id=0,
        posicao=(1, 2),
    )

    destino_inexistente = NoAbstrato(
        cluster_id=99,
        posicao=(99, 99),
    )

    resultado = buscar_no_grafo_abstrato(
        grafo=grafo,
        inicio=inicio,
        destino=destino_inexistente,
    )

    assert resultado.encontrado is False
    assert resultado.nos == []
    assert resultado.arestas == []