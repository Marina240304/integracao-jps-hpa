from src.grid import Grid
from src.hpa import (
    dividir_em_clusters,
    encontrar_cluster,
    identificar_portais,
)


def test_divisao_em_quatro_clusters() -> None:
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

    assert len(clusters) == 4

    assert encontrar_cluster(
        clusters,
        (0, 0),
    ).identificador == 0

    assert encontrar_cluster(
        clusters,
        (0, 5),
    ).identificador == 1

    assert encontrar_cluster(
        clusters,
        (5, 0),
    ).identificador == 2

    assert encontrar_cluster(
        clusters,
        (5, 5),
    ).identificador == 3


def test_clusters_em_mapa_nao_divisivel() -> None:
    matriz = [
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
    ]

    grid = Grid.criar(matriz)

    clusters = dividir_em_clusters(
        grid=grid,
        tamanho_cluster=3,
    )

    assert len(clusters) == 4

    ultimo_cluster = clusters[3]

    assert ultimo_cluster.linha_inicio == 3
    assert ultimo_cluster.linha_fim == 5
    assert ultimo_cluster.coluna_inicio == 3
    assert ultimo_cluster.coluna_fim == 5

    from src.hpa import identificar_portais


def test_portal_em_fronteira_vertical_livre() -> None:
    matriz = [
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

    assert len(portais) == 1

    portal = portais[0]

    assert portal.cluster_origem == 0
    assert portal.cluster_destino == 1
    assert portal.posicao_origem == (1, 2)
    assert portal.posicao_destino == (1, 3)


def test_duas_passagens_separadas_criam_dois_portais() -> None:
    matriz = [
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 0],
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

    assert len(portais) == 2

    assert portais[0].posicao_origem == (0, 2)
    assert portais[0].posicao_destino == (0, 3)

    assert portais[1].posicao_origem == (2, 2)
    assert portais[1].posicao_destino == (2, 3)