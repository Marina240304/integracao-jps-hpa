from math import isclose

from src.astar import buscar_caminho
from src.grid import Grid


def test_astar_encontra_caminho_reto() -> None:
    matriz = [
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
    ]

    grid = Grid.criar(matriz)

    resultado = buscar_caminho(
        grid=grid,
        inicio=(0, 0),
        destino=(0, 2),
    )

    assert resultado.encontrado is True
    assert resultado.caminho[0] == (0, 0)
    assert resultado.caminho[-1] == (0, 2)
    assert isclose(resultado.custo, 2.0)


def test_astar_nao_encontra_caminho_bloqueado() -> None:
    matriz = [
        [0, 1, 0],
        [1, 1, 1],
        [0, 1, 0],
    ]

    grid = Grid.criar(matriz)

    resultado = buscar_caminho(
        grid=grid,
        inicio=(0, 0),
        destino=(2, 2),
    )

    assert resultado.encontrado is False
    assert resultado.caminho == []