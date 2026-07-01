from math import isclose, sqrt

from src.grafo_abstrato import (
    NoAbstrato,
    construir_grafo_abstrato,
)
from src.grid import Grid
from src.hpa import (
    dividir_em_clusters,
    identificar_portais,
)


def criar_grafo_de_teste():
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

    return grafo, portais


def test_grafo_abstrato_possui_nos_e_arestas() -> None:
    grafo, portais = criar_grafo_de_teste()

    assert len(portais) == 4

    assert grafo.quantidade_nos == 8

    assert grafo.quantidade_arestas == 8


def test_conexao_entre_clusters() -> None:
    grafo, _ = criar_grafo_de_teste()

    no_cluster_a = NoAbstrato(
        cluster_id=0,
        posicao=(1, 2),
    )

    no_cluster_b = NoAbstrato(
        cluster_id=1,
        posicao=(1, 3),
    )

    arestas = grafo.vizinhos(no_cluster_a)

    aresta_portal = next(
        aresta
        for aresta in arestas
        if (
            aresta.destino == no_cluster_b
            and aresta.tipo == "inter_cluster"
        )
    )

    assert isclose(
        aresta_portal.custo,
        1.0,
    )

    assert aresta_portal.caminho == (
        (1, 2),
        (1, 3),
    )


def test_conexao_dentro_do_cluster() -> None:
    grafo, _ = criar_grafo_de_teste()

    no_direita = NoAbstrato(
        cluster_id=0,
        posicao=(1, 2),
    )

    no_inferior = NoAbstrato(
        cluster_id=0,
        posicao=(2, 1),
    )

    aresta_interna = next(
        aresta
        for aresta in grafo.vizinhos(no_direita)
        if (
            aresta.destino == no_inferior
            and aresta.tipo == "intra_cluster"
        )
    )

    assert isclose(
        aresta_interna.custo,
        sqrt(2),
    )

    assert aresta_interna.caminho == (
        (1, 2),
        (2, 1),
    )