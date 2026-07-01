from dataclasses import dataclass

from src.grid import Grid, Posicao


@dataclass(frozen=True, slots=True)
class Cluster:
    """
    Representa uma região retangular do grid.

    linha_fim e coluna_fim não pertencem ao intervalo.
    """

    identificador: int
    linha_cluster: int
    coluna_cluster: int
    linha_inicio: int
    linha_fim: int
    coluna_inicio: int
    coluna_fim: int

    def contem(self, posicao: Posicao) -> bool:
        linha, coluna = posicao

        return (
            self.linha_inicio <= linha < self.linha_fim
            and self.coluna_inicio <= coluna < self.coluna_fim
        )


@dataclass(frozen=True, slots=True)
class Portal:
    """
    Representa uma passagem entre dois clusters vizinhos.

    posicao_origem pertence ao primeiro cluster.
    posicao_destino pertence ao segundo cluster.
    """

    cluster_origem: int
    cluster_destino: int
    posicao_origem: Posicao
    posicao_destino: Posicao


def dividir_em_clusters(
    grid: Grid,
    tamanho_cluster: int,
) -> list[Cluster]:
    """
    Divide o grid em regiões retangulares.
    """

    if tamanho_cluster <= 0:
        raise ValueError(
            "O tamanho do cluster deve ser maior que zero."
        )

    clusters: list[Cluster] = []

    identificador = 0
    linha_cluster = 0

    for linha_inicio in range(
        0,
        grid.quantidade_linhas,
        tamanho_cluster,
    ):
        linha_fim = min(
            linha_inicio + tamanho_cluster,
            grid.quantidade_linhas,
        )

        coluna_cluster = 0

        for coluna_inicio in range(
            0,
            grid.quantidade_colunas,
            tamanho_cluster,
        ):
            coluna_fim = min(
                coluna_inicio + tamanho_cluster,
                grid.quantidade_colunas,
            )

            clusters.append(
                Cluster(
                    identificador=identificador,
                    linha_cluster=linha_cluster,
                    coluna_cluster=coluna_cluster,
                    linha_inicio=linha_inicio,
                    linha_fim=linha_fim,
                    coluna_inicio=coluna_inicio,
                    coluna_fim=coluna_fim,
                )
            )

            identificador += 1
            coluna_cluster += 1

        linha_cluster += 1

    return clusters


def encontrar_cluster(
    clusters: list[Cluster],
    posicao: Posicao,
) -> Cluster | None:
    """
    Retorna o cluster que contém uma posição.
    """

    for cluster in clusters:
        if cluster.contem(posicao):
            return cluster

    return None


def _agrupar_passagens(
    passagens: list[tuple[Posicao, Posicao]],
) -> list[list[tuple[Posicao, Posicao]]]:
    """
    Agrupa células consecutivas de uma mesma fronteira.

    Cada grupo representa uma passagem contínua.
    """

    if not passagens:
        return []

    grupos: list[list[tuple[Posicao, Posicao]]] = []
    grupo_atual = [passagens[0]]

    for passagem in passagens[1:]:
        origem_anterior = grupo_atual[-1][0]
        origem_atual = passagem[0]

        diferenca_linha = abs(
            origem_atual[0] - origem_anterior[0]
        )

        diferenca_coluna = abs(
            origem_atual[1] - origem_anterior[1]
        )

        sao_consecutivas = (
            diferenca_linha + diferenca_coluna == 1
        )

        if sao_consecutivas:
            grupo_atual.append(passagem)
        else:
            grupos.append(grupo_atual)
            grupo_atual = [passagem]

    grupos.append(grupo_atual)

    return grupos


def _criar_portal_do_grupo(
    grupo: list[tuple[Posicao, Posicao]],
    cluster_origem: Cluster,
    cluster_destino: Cluster,
) -> Portal:
    """
    Escolhe a passagem central de um grupo contínuo.
    """

    indice_central = len(grupo) // 2

    posicao_origem, posicao_destino = grupo[indice_central]

    return Portal(
        cluster_origem=cluster_origem.identificador,
        cluster_destino=cluster_destino.identificador,
        posicao_origem=posicao_origem,
        posicao_destino=posicao_destino,
    )


def _portais_entre_clusters_lado_a_lado(
    grid: Grid,
    cluster_esquerdo: Cluster,
    cluster_direito: Cluster,
) -> list[Portal]:
    """
    Detecta portais entre clusters separados
    por uma fronteira vertical.
    """

    coluna_esquerda = cluster_esquerdo.coluna_fim - 1
    coluna_direita = cluster_direito.coluna_inicio

    linha_inicio = max(
        cluster_esquerdo.linha_inicio,
        cluster_direito.linha_inicio,
    )

    linha_fim = min(
        cluster_esquerdo.linha_fim,
        cluster_direito.linha_fim,
    )

    passagens: list[tuple[Posicao, Posicao]] = []

    for linha in range(linha_inicio, linha_fim):
        posicao_esquerda = (
            linha,
            coluna_esquerda,
        )

        posicao_direita = (
            linha,
            coluna_direita,
        )

        if (
            grid.esta_livre(posicao_esquerda)
            and grid.esta_livre(posicao_direita)
        ):
            passagens.append(
                (
                    posicao_esquerda,
                    posicao_direita,
                )
            )

    grupos = _agrupar_passagens(passagens)

    return [
        _criar_portal_do_grupo(
            grupo,
            cluster_esquerdo,
            cluster_direito,
        )
        for grupo in grupos
    ]


def _portais_entre_clusters_um_sobre_o_outro(
    grid: Grid,
    cluster_superior: Cluster,
    cluster_inferior: Cluster,
) -> list[Portal]:
    """
    Detecta portais entre clusters separados
    por uma fronteira horizontal.
    """

    linha_superior = cluster_superior.linha_fim - 1
    linha_inferior = cluster_inferior.linha_inicio

    coluna_inicio = max(
        cluster_superior.coluna_inicio,
        cluster_inferior.coluna_inicio,
    )

    coluna_fim = min(
        cluster_superior.coluna_fim,
        cluster_inferior.coluna_fim,
    )

    passagens: list[tuple[Posicao, Posicao]] = []

    for coluna in range(coluna_inicio, coluna_fim):
        posicao_superior = (
            linha_superior,
            coluna,
        )

        posicao_inferior = (
            linha_inferior,
            coluna,
        )

        if (
            grid.esta_livre(posicao_superior)
            and grid.esta_livre(posicao_inferior)
        ):
            passagens.append(
                (
                    posicao_superior,
                    posicao_inferior,
                )
            )

    grupos = _agrupar_passagens(passagens)

    return [
        _criar_portal_do_grupo(
            grupo,
            cluster_superior,
            cluster_inferior,
        )
        for grupo in grupos
    ]


def identificar_portais(
    grid: Grid,
    clusters: list[Cluster],
) -> list[Portal]:
    """
    Identifica portais entre todos os clusters vizinhos.

    São verificadas somente as fronteiras à direita
    e abaixo de cada cluster, evitando duplicações.
    """

    clusters_por_posicao = {
        (
            cluster.linha_cluster,
            cluster.coluna_cluster,
        ): cluster
        for cluster in clusters
    }

    portais: list[Portal] = []

    for cluster in clusters:
        cluster_direito = clusters_por_posicao.get(
            (
                cluster.linha_cluster,
                cluster.coluna_cluster + 1,
            )
        )

        if cluster_direito is not None:
            portais.extend(
                _portais_entre_clusters_lado_a_lado(
                    grid,
                    cluster,
                    cluster_direito,
                )
            )

        cluster_inferior = clusters_por_posicao.get(
            (
                cluster.linha_cluster + 1,
                cluster.coluna_cluster,
            )
        )

        if cluster_inferior is not None:
            portais.extend(
                _portais_entre_clusters_um_sobre_o_outro(
                    grid,
                    cluster,
                    cluster_inferior,
                )
            )

    return portais