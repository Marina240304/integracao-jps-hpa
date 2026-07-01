from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from typing import Iterator, TypeAlias


Posicao: TypeAlias = tuple[int, int]


@dataclass(frozen=True, slots=True)
class Grid:
    """
    Representa o mapa 5x5

    Valores:
        0 = posição livre
        1 = obstáculo
    """

    celulas: tuple[tuple[int, ...], ...]

    def __post_init__(self) -> None:
        if not self.celulas:
            raise ValueError("O grid não pode estar vazio.")

        quantidade_colunas = len(self.celulas[0])

        if quantidade_colunas == 0:
            raise ValueError("O grid deve possuir pelo menos uma coluna.")

        for linha in self.celulas:
            if len(linha) != quantidade_colunas:
                raise ValueError("Todas as linhas devem ter o mesmo tamanho.")

            if any(valor not in (0, 1) for valor in linha):
                raise ValueError("O grid pode conter somente os valores 0 e 1.")

    @classmethod
    def criar(cls, matriz: list[list[int]]) -> Grid:
        """
        Converte uma lista de listas em uma instância imutável de Grid.
        """
        return cls(tuple(tuple(linha) for linha in matriz))

    @property
    def quantidade_linhas(self) -> int:
        return len(self.celulas)

    @property
    def quantidade_colunas(self) -> int:
        return len(self.celulas[0])

    def esta_dentro(self, posicao: Posicao) -> bool:
        linha, coluna = posicao

        return (
            0 <= linha < self.quantidade_linhas
            and 0 <= coluna < self.quantidade_colunas
        )

    def esta_livre(self, posicao: Posicao) -> bool:
        if not self.esta_dentro(posicao):
            return False

        linha, coluna = posicao
        return self.celulas[linha][coluna] == 0

    def vizinhos(
        self,
        posicao: Posicao,
        permitir_diagonal: bool = True,
    ) -> Iterator[tuple[Posicao, float]]:
        """
        Retorna as posições vizinhas livres e o custo de cada movimento.

        Movimentos retos custam 1.
        Movimentos diagonais custam sqrt(2).

        Não é permitido atravessar diagonalmente o canto de obstáculos.
        """

        linha_atual, coluna_atual = posicao

        direcoes = [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),
        ]

        if permitir_diagonal:
            direcoes.extend(
                [
                    (-1, -1),
                    (-1, 1),
                    (1, -1),
                    (1, 1),
                ]
            )

        for deslocamento_linha, deslocamento_coluna in direcoes:
            nova_posicao = (
                linha_atual + deslocamento_linha,
                coluna_atual + deslocamento_coluna,
            )

            if not self.esta_livre(nova_posicao):
                continue

            movimento_diagonal = (
                deslocamento_linha != 0
                and deslocamento_coluna != 0
            )

            if movimento_diagonal:
                vizinho_vertical = (
                    linha_atual + deslocamento_linha,
                    coluna_atual,
                )

                vizinho_horizontal = (
                    linha_atual,
                    coluna_atual + deslocamento_coluna,
                )

                if not self.esta_livre(vizinho_vertical):
                    continue

                if not self.esta_livre(vizinho_horizontal):
                    continue

                custo = sqrt(2)
            else:
                custo = 1.0

            yield nova_posicao, custo