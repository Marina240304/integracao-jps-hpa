from math import isclose, isinf, sqrt

from src.grid import Grid
from src.hpa_busca import buscar_hpa
from src.hpa_jps import buscar_hpa_jps


def calcular_custo_do_caminho(
    caminho: list[tuple[int, int]],
) -> float:
    custo = 0.0

    for atual, proxima in zip(
        caminho,
        caminho[1:],
    ):
        diferenca_linha = abs(
            atual[0] - proxima[0]
        )

        diferenca_coluna = abs(
            atual[1] - proxima[1]
        )

        if (
            diferenca_linha == 1
            and diferenca_coluna == 1
        ):
            custo += sqrt(2)
        else:
            custo += 1.0

    return custo


def test_hpa_jps_encontra_caminho() -> None:
    matriz = [
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
    ]

    grid = Grid.criar(matriz)

    resultado = buscar_hpa_jps(
        grid=grid,
        inicio=(0, 0),
        destino=(5, 5),
        tamanho_cluster=3,
    )

    assert resultado.encontrado is True

    assert resultado.caminho[0] == (0, 0)
    assert resultado.caminho[-1] == (5, 5)

    assert resultado.quantidade_portais == 4
    assert resultado.tamanho_grafo_abstrato >= 8
    assert resultado.nos_expandidos > 0

    assert resultado.jump_points_identificados > 0

    custo_caminho = calcular_custo_do_caminho(
        resultado.caminho
    )

    assert isclose(
        resultado.custo,
        custo_caminho,
    )


def test_hpa_e_hpa_jps_possuem_mesmo_custo() -> None:
    matriz = [
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
    ]

    grid = Grid.criar(matriz)

    resultado_hpa = buscar_hpa(
        grid=grid,
        inicio=(0, 0),
        destino=(5, 5),
        tamanho_cluster=3,
    )

    resultado_hpa_jps = buscar_hpa_jps(
        grid=grid,
        inicio=(0, 0),
        destino=(5, 5),
        tamanho_cluster=3,
    )

    assert resultado_hpa.encontrado is True
    assert resultado_hpa_jps.encontrado is True

    assert isclose(
        resultado_hpa.custo,
        resultado_hpa_jps.custo,
    )


def test_hpa_jps_falha_com_inicio_bloqueado() -> None:
    matriz = [
        [1, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
    ]

    grid = Grid.criar(matriz)

    resultado = buscar_hpa_jps(
        grid=grid,
        inicio=(0, 0),
        destino=(2, 2),
        tamanho_cluster=3,
    )

    assert resultado.encontrado is False
    assert resultado.caminho == []
    assert isinf(resultado.custo)