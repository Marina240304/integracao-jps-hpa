from math import isclose

from src.astar import buscar_caminho
from src.grid import Grid
from src.jps import buscar_caminho_jps


def test_jps_encontra_mesmo_custo_do_astar() -> None:
    matriz = [
        [0, 0, 0, 0, 0],
        [0, 1, 0, 1, 0],
        [0, 1, 0, 0, 0],
        [0, 0, 0, 1, 0],
        [0, 0, 0, 0, 0],
    ]

    grid = Grid.criar(matriz)

    inicio = (4, 0)
    destino = (0, 4)

    resultado_astar = buscar_caminho(
        grid,
        inicio,
        destino,
    )

    resultado_jps = buscar_caminho_jps(
        grid,
        inicio,
        destino,
    )

    assert resultado_jps.encontrado is True

    assert resultado_jps.caminho[0] == inicio

    assert resultado_jps.caminho[-1] == destino

    assert isclose(
        resultado_jps.custo,
        resultado_astar.custo,
    )


def test_jps_nao_encontra_caminho_bloqueado() -> None:
    matriz = [
        [0, 1, 0],
        [1, 1, 1],
        [0, 1, 0],
    ]

    grid = Grid.criar(matriz)

    resultado = buscar_caminho_jps(
        grid,
        inicio=(0, 0),
        destino=(2, 2),
    )

    assert resultado.encontrado is False
    assert resultado.caminho == []
    