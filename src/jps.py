from dataclasses import dataclass
from heapq import heappop, heappush
from itertools import count
from math import inf
from time import perf_counter

from src.astar import heuristica_octil
from src.grid import Grid, Posicao


@dataclass
class ResultadoJPS:
    encontrado: bool
    caminho: list[Posicao]
    custo: float
    nos_expandidos: int
    tempo_segundos: float
    jump_points_identificados: int


def sinal(valor: int) -> int:
    """
    Retorna a direção de um valor.

    Valor negativo: -1
    Valor zero:      0
    Valor positivo:  1
    """

    if valor < 0:
        return -1

    if valor > 0:
        return 1

    return 0


def movimento_valido(
    grid: Grid,
    origem: Posicao,
    deslocamento_linha: int,
    deslocamento_coluna: int,
) -> bool:
    """
    Verifica se é possível realizar um movimento.

    Movimentos diagonais não podem atravessar
    o canto de obstáculos.
    """

    linha, coluna = origem

    destino = (
        linha + deslocamento_linha,
        coluna + deslocamento_coluna,
    )

    if not grid.esta_livre(destino):
        return False

    movimento_diagonal = (
        deslocamento_linha != 0
        and deslocamento_coluna != 0
    )

    if movimento_diagonal:
        vizinho_vertical = (
            linha + deslocamento_linha,
            coluna,
        )

        vizinho_horizontal = (
            linha,
            coluna + deslocamento_coluna,
        )

        if not grid.esta_livre(vizinho_vertical):
            return False

        if not grid.esta_livre(vizinho_horizontal):
            return False

    return True


def direcoes_forcadas(
    grid: Grid,
    posicao: Posicao,
    deslocamento_linha: int,
    deslocamento_coluna: int,
) -> list[tuple[int, int]]:
    """
    Identifica direções que se tornam obrigatórias
    devido à presença de obstáculos.

    Essas direções indicam a existência de um
    possível Jump Point.
    """

    linha, coluna = posicao
    direcoes: list[tuple[int, int]] = []

    # Movimento vertical
    if deslocamento_linha != 0 and deslocamento_coluna == 0:
        for lado in (-1, 1):
            lateral_do_pai = (
                linha - deslocamento_linha,
                coluna + lado,
            )

            lateral_atual = (
                linha,
                coluna + lado,
            )

            if (
                not grid.esta_livre(lateral_do_pai)
                and grid.esta_livre(lateral_atual)
            ):
                direcoes.append((0, lado))

                if movimento_valido(
                    grid,
                    posicao,
                    deslocamento_linha,
                    lado,
                ):
                    direcoes.append(
                        (deslocamento_linha, lado)
                    )

    # Movimento horizontal
    elif deslocamento_coluna != 0 and deslocamento_linha == 0:
        for lado in (-1, 1):
            lateral_do_pai = (
                linha + lado,
                coluna - deslocamento_coluna,
            )

            lateral_atual = (
                linha + lado,
                coluna,
            )

            if (
                not grid.esta_livre(lateral_do_pai)
                and grid.esta_livre(lateral_atual)
            ):
                direcoes.append((lado, 0))

                if movimento_valido(
                    grid,
                    posicao,
                    lado,
                    deslocamento_coluna,
                ):
                    direcoes.append(
                        (lado, deslocamento_coluna)
                    )

    return direcoes


def possui_vizinho_forcado(
    grid: Grid,
    posicao: Posicao,
    deslocamento_linha: int,
    deslocamento_coluna: int,
) -> bool:
    return bool(
        direcoes_forcadas(
            grid,
            posicao,
            deslocamento_linha,
            deslocamento_coluna,
        )
    )


def todas_direcoes_validas(
    grid: Grid,
    posicao: Posicao,
) -> list[tuple[int, int]]:
    direcoes: list[tuple[int, int]] = []

    for deslocamento_linha in (-1, 0, 1):
        for deslocamento_coluna in (-1, 0, 1):
            if (
                deslocamento_linha == 0
                and deslocamento_coluna == 0
            ):
                continue

            if movimento_valido(
                grid,
                posicao,
                deslocamento_linha,
                deslocamento_coluna,
            ):
                direcoes.append(
                    (
                        deslocamento_linha,
                        deslocamento_coluna,
                    )
                )

    return direcoes


def direcoes_sucessoras(
    grid: Grid,
    posicao: Posicao,
    pai: Posicao | None,
) -> list[tuple[int, int]]:
    """
    Retorna as direções naturais e forçadas
    que ainda precisam ser pesquisadas.
    """

    if pai is None:
        return todas_direcoes_validas(
            grid,
            posicao,
        )

    linha, coluna = posicao
    linha_pai, coluna_pai = pai

    deslocamento_linha = sinal(
        linha - linha_pai
    )

    deslocamento_coluna = sinal(
        coluna - coluna_pai
    )

    direcoes: list[tuple[int, int]] = []

    def adicionar(
        direcao: tuple[int, int],
    ) -> None:
        if direcao in direcoes:
            return

        if movimento_valido(
            grid,
            posicao,
            direcao[0],
            direcao[1],
        ):
            direcoes.append(direcao)

    movimento_diagonal = (
        deslocamento_linha != 0
        and deslocamento_coluna != 0
    )

    if movimento_diagonal:
        adicionar(
            (deslocamento_linha, 0)
        )

        adicionar(
            (0, deslocamento_coluna)
        )

        adicionar(
            (
                deslocamento_linha,
                deslocamento_coluna,
            )
        )

    else:
        adicionar(
            (
                deslocamento_linha,
                deslocamento_coluna,
            )
        )

        for direcao in direcoes_forcadas(
            grid,
            posicao,
            deslocamento_linha,
            deslocamento_coluna,
        ):
            adicionar(direcao)

    return direcoes


def pular(
    grid: Grid,
    origem: Posicao,
    deslocamento_linha: int,
    deslocamento_coluna: int,
    destino: Posicao,
) -> Posicao | None:
    """
    Avança em uma direção até encontrar:

    - o destino;
    - um Jump Point;
    - ou um obstáculo.
    """

    posicao_atual = origem

    while movimento_valido(
        grid,
        posicao_atual,
        deslocamento_linha,
        deslocamento_coluna,
    ):
        posicao_atual = (
            posicao_atual[0] + deslocamento_linha,
            posicao_atual[1] + deslocamento_coluna,
        )

        if posicao_atual == destino:
            return posicao_atual

        if possui_vizinho_forcado(
            grid,
            posicao_atual,
            deslocamento_linha,
            deslocamento_coluna,
        ):
            return posicao_atual

        movimento_diagonal = (
            deslocamento_linha != 0
            and deslocamento_coluna != 0
        )

        if movimento_diagonal:
            salto_vertical = pular(
                grid,
                posicao_atual,
                deslocamento_linha,
                0,
                destino,
            )

            salto_horizontal = pular(
                grid,
                posicao_atual,
                0,
                deslocamento_coluna,
                destino,
            )

            if (
                salto_vertical is not None
                or salto_horizontal is not None
            ):
                return posicao_atual

    return None


def expandir_segmento(
    origem: Posicao,
    destino: Posicao,
) -> list[Posicao]:
    """
    Converte um salto em uma sequência de células.
    """

    deslocamento_linha = sinal(
        destino[0] - origem[0]
    )

    deslocamento_coluna = sinal(
        destino[1] - origem[1]
    )

    segmento: list[Posicao] = []
    posicao_atual = origem

    while posicao_atual != destino:
        posicao_atual = (
            posicao_atual[0] + deslocamento_linha,
            posicao_atual[1] + deslocamento_coluna,
        )

        segmento.append(posicao_atual)

    return segmento


def reconstruir_caminho(
    anteriores: dict[Posicao, Posicao],
    inicio: Posicao,
    destino: Posicao,
) -> list[Posicao]:
    """
    Reconstrói primeiro a sequência de Jump Points
    e depois inclui as células intermediárias.
    """

    pontos_salto = [destino]
    posicao_atual = destino

    while posicao_atual != inicio:
        posicao_atual = anteriores[posicao_atual]
        pontos_salto.append(posicao_atual)

    pontos_salto.reverse()

    caminho_completo = [pontos_salto[0]]

    for indice in range(
        len(pontos_salto) - 1
    ):
        origem = pontos_salto[indice]
        proximo = pontos_salto[indice + 1]

        caminho_completo.extend(
            expandir_segmento(
                origem,
                proximo,
            )
        )

    return caminho_completo


def buscar_caminho_jps(
    grid: Grid,
    inicio: Posicao,
    destino: Posicao,
) -> ResultadoJPS:
    """
    Executa o algoritmo Jump Point Search.
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

    heappush(
        fila_prioridade,
        (
            heuristica_octil(
                inicio,
                destino,
            ),
            next(contador),
            inicio,
        ),
    )

    custos: dict[Posicao, float] = {
        inicio: 0.0
    }

    anteriores: dict[Posicao, Posicao] = {}

    visitados: set[Posicao] = set()

    jump_points: set[Posicao] = set()

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
                inicio,
                destino,
            )

            return ResultadoJPS(
                encontrado=True,
                caminho=caminho,
                custo=custos[destino],
                nos_expandidos=nos_expandidos,
                tempo_segundos=tempo_total,
                jump_points_identificados=len(
                    jump_points
                ),
            )

        pai = anteriores.get(
            posicao_atual
        )

        for (
            deslocamento_linha,
            deslocamento_coluna,
        ) in direcoes_sucessoras(
            grid,
            posicao_atual,
            pai,
        ):
            ponto_salto = pular(
                grid,
                posicao_atual,
                deslocamento_linha,
                deslocamento_coluna,
                destino,
            )

            if ponto_salto is None:
                continue

            jump_points.add(ponto_salto)

            custo_salto = heuristica_octil(
                posicao_atual,
                ponto_salto,
            )

            novo_custo = (
                custos[posicao_atual]
                + custo_salto
            )

            custo_anterior = custos.get(
                ponto_salto,
                inf,
            )

            if novo_custo < custo_anterior:
                custos[ponto_salto] = novo_custo
                anteriores[ponto_salto] = (
                    posicao_atual
                )

                prioridade = (
                    novo_custo
                    + heuristica_octil(
                        ponto_salto,
                        destino,
                    )
                )

                heappush(
                    fila_prioridade,
                    (
                        prioridade,
                        next(contador),
                        ponto_salto,
                    ),
                )

    tempo_total = perf_counter() - tempo_inicial

    return ResultadoJPS(
        encontrado=False,
        caminho=[],
        custo=inf,
        nos_expandidos=nos_expandidos,
        tempo_segundos=tempo_total,
        jump_points_identificados=len(
            jump_points
        ),
    )