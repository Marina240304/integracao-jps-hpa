from dataclasses import dataclass, field
from itertools import combinations

from src.astar import buscar_caminho
from src.grid import Grid, Posicao
from src.hpa import Cluster, Portal


@dataclass(frozen=True, slots=True)
class NoAbstrato:
    """
    Representa um nó do grafo abstrato.

    Cada nó corresponde a uma célula de portal
    pertencente a determinado cluster.
    """

    cluster_id: int
    posicao: Posicao


@dataclass(frozen=True, slots=True)
class ArestaAbstrata:
    """
    Representa uma conexão entre dois nós abstratos.
    """

    destino: NoAbstrato
    custo: float
    caminho: tuple[Posicao, ...]
    tipo: str


@dataclass(slots=True)
class GrafoAbstrato:
    """
    Armazena os nós e as conexões do grafo abstrato.
    """

    adjacencias: dict[
        NoAbstrato,
        list[ArestaAbstrata],
    ] = field(default_factory=dict)

    def adicionar_no(
        self,
        no: NoAbstrato,
    ) -> None:
        self.adjacencias.setdefault(no, [])

    def _adicionar_aresta_unidirecional(
        self,
        origem: NoAbstrato,
        destino: NoAbstrato,
        custo: float,
        caminho: tuple[Posicao, ...],
        tipo: str,
    ) -> None:
        self.adicionar_no(origem)
        self.adicionar_no(destino)

        aresta_ja_existe = any(
            aresta.destino == destino
            and aresta.tipo == tipo
            for aresta in self.adjacencias[origem]
        )

        if aresta_ja_existe:
            return

        self.adjacencias[origem].append(
            ArestaAbstrata(
                destino=destino,
                custo=custo,
                caminho=caminho,
                tipo=tipo,
            )
        )

    def adicionar_aresta_bidirecional(
        self,
        origem: NoAbstrato,
        destino: NoAbstrato,
        custo: float,
        caminho: list[Posicao] | tuple[Posicao, ...],
        tipo: str,
    ) -> None:
        """
        Adiciona uma conexão que pode ser percorrida
        nos dois sentidos.
        """

        caminho_tupla = tuple(caminho)

        self._adicionar_aresta_unidirecional(
            origem=origem,
            destino=destino,
            custo=custo,
            caminho=caminho_tupla,
            tipo=tipo,
        )

        self._adicionar_aresta_unidirecional(
            origem=destino,
            destino=origem,
            custo=custo,
            caminho=tuple(reversed(caminho_tupla)),
            tipo=tipo,
        )

    def vizinhos(
        self,
        no: NoAbstrato,
    ) -> list[ArestaAbstrata]:
        return self.adjacencias.get(no, [])

    @property
    def quantidade_nos(self) -> int:
        return len(self.adjacencias)

    @property
    def quantidade_arestas(self) -> int:
        """
        Como todas as arestas são bidirecionais,
        divide-se a quantidade por dois.
        """

        quantidade_direcionada = sum(
            len(arestas)
            for arestas in self.adjacencias.values()
        )

        return quantidade_direcionada // 2


def criar_grid_restrito_ao_cluster(
    grid: Grid,
    cluster: Cluster,
) -> Grid:
    """
    Cria uma cópia do grid em que somente as células
    pertencentes ao cluster podem ser utilizadas.

    As células externas são tratadas como obstáculos.
    """

    matriz: list[list[int]] = []

    for linha in range(grid.quantidade_linhas):
        nova_linha: list[int] = []

        for coluna in range(grid.quantidade_colunas):
            posicao = (linha, coluna)

            if (
                cluster.contem(posicao)
                and grid.esta_livre(posicao)
            ):
                nova_linha.append(0)
            else:
                nova_linha.append(1)

        matriz.append(nova_linha)

    return Grid.criar(matriz)


def construir_grafo_abstrato(
    grid: Grid,
    clusters: list[Cluster],
    portais: list[Portal],
) -> GrafoAbstrato:
    """
    Constrói o grafo abstrato do HPA*.

    Primeiro cria as conexões entre clusters pelos
    portais. Depois conecta, dentro de cada cluster,
    os nós de portal que possuem caminho entre si.
    """

    grafo = GrafoAbstrato()

    nos_por_cluster: dict[
        int,
        set[NoAbstrato],
    ] = {}

    # Cria os nós dos portais e as conexões
    # que atravessam as fronteiras.
    for portal in portais:
        no_origem = NoAbstrato(
            cluster_id=portal.cluster_origem,
            posicao=portal.posicao_origem,
        )

        no_destino = NoAbstrato(
            cluster_id=portal.cluster_destino,
            posicao=portal.posicao_destino,
        )

        grafo.adicionar_no(no_origem)
        grafo.adicionar_no(no_destino)

        nos_por_cluster.setdefault(
            portal.cluster_origem,
            set(),
        ).add(no_origem)

        nos_por_cluster.setdefault(
            portal.cluster_destino,
            set(),
        ).add(no_destino)

        grafo.adicionar_aresta_bidirecional(
            origem=no_origem,
            destino=no_destino,
            custo=1.0,
            caminho=[
                portal.posicao_origem,
                portal.posicao_destino,
            ],
            tipo="inter_cluster",
        )

    clusters_por_id = {
        cluster.identificador: cluster
        for cluster in clusters
    }

    # Conecta os portais pertencentes ao mesmo cluster.
    for cluster_id, conjunto_nos in nos_por_cluster.items():
        cluster = clusters_por_id[cluster_id]

        grid_restrito = criar_grid_restrito_ao_cluster(
            grid=grid,
            cluster=cluster,
        )

        nos_do_cluster = list(conjunto_nos)

        for no_origem, no_destino in combinations(
            nos_do_cluster,
            2,
        ):
            resultado = buscar_caminho(
                grid=grid_restrito,
                inicio=no_origem.posicao,
                destino=no_destino.posicao,
            )

            if not resultado.encontrado:
                continue

            grafo.adicionar_aresta_bidirecional(
                origem=no_origem,
                destino=no_destino,
                custo=resultado.custo,
                caminho=resultado.caminho,
                tipo="intra_cluster",
            )

    return grafo