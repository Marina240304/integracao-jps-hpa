from dataclasses import dataclass
from math import inf
from time import perf_counter

from src.astar import buscar_caminho
from src.busca_abstrata import (
    buscar_no_grafo_abstrato,
    montar_caminho_do_grid,
)
from src.grafo_abstrato import (
    GrafoAbstrato,
    NoAbstrato,
    construir_grafo_abstrato,
    criar_grid_restrito_ao_cluster,
)
from src.grid import Grid, Posicao
from src.hpa import (
    Cluster,
    dividir_em_clusters,
    encontrar_cluster,
    identificar_portais,
)


@dataclass(slots=True)
class ResultadoHPA:
    """
    Resultado completo da busca HPA*.
    """

    encontrado: bool
    caminho: list[Posicao]
    custo: float
    nos_expandidos: int
    nos_expandidos_abstratos: int
    tempo_segundos: float
    quantidade_portais: int
    tamanho_grafo_abstrato: int
    quantidade_arestas_abstratas: int


def conectar_posicao_ao_cluster(
    grafo: GrafoAbstrato,
    grid: Grid,
    cluster: Cluster,
    no_posicao: NoAbstrato,
) -> int:
    """
    Conecta uma posição temporária aos nós de portal
    pertencentes ao mesmo cluster.

    Retorna a quantidade de nós expandidos pelas
    buscas locais.
    """

    grafo.adicionar_no(no_posicao)

    grid_restrito = criar_grid_restrito_ao_cluster(
        grid=grid,
        cluster=cluster,
    )

    nos_expandidos = 0

    nos_do_cluster = [
        no
        for no in list(grafo.adjacencias.keys())
        if (
            no.cluster_id == cluster.identificador
            and no != no_posicao
        )
    ]

    for no_portal in nos_do_cluster:
        resultado = buscar_caminho(
            grid=grid_restrito,
            inicio=no_posicao.posicao,
            destino=no_portal.posicao,
        )

        nos_expandidos += resultado.nos_expandidos

        if not resultado.encontrado:
            continue

        grafo.adicionar_aresta_bidirecional(
            origem=no_posicao,
            destino=no_portal,
            custo=resultado.custo,
            caminho=resultado.caminho,
            tipo="conexao_consulta",
        )

    return nos_expandidos


def conectar_inicio_ao_destino_no_mesmo_cluster(
    grafo: GrafoAbstrato,
    grid: Grid,
    cluster: Cluster,
    no_inicio: NoAbstrato,
    no_destino: NoAbstrato,
) -> int:
    """
    Cria uma conexão direta quando início e destino
    pertencem ao mesmo cluster.
    """

    grid_restrito = criar_grid_restrito_ao_cluster(
        grid=grid,
        cluster=cluster,
    )

    resultado = buscar_caminho(
        grid=grid_restrito,
        inicio=no_inicio.posicao,
        destino=no_destino.posicao,
    )

    if resultado.encontrado:
        grafo.adicionar_aresta_bidirecional(
            origem=no_inicio,
            destino=no_destino,
            custo=resultado.custo,
            caminho=resultado.caminho,
            tipo="conexao_direta",
        )

    return resultado.nos_expandidos


def buscar_hpa(
    grid: Grid,
    inicio: Posicao,
    destino: Posicao,
    tamanho_cluster: int,
) -> ResultadoHPA:
    """
    Executa o HPA* completo.

    Etapas:
    1. Divide o mapa em clusters;
    2. Identifica os portais;
    3. Constrói o grafo abstrato;
    4. Conecta início e destino ao grafo;
    5. Executa A* no grafo abstrato;
    6. Reconstrói o caminho detalhado.
    """

    tempo_inicio = perf_counter()

    if (
        not grid.esta_dentro(inicio)
        or not grid.esta_dentro(destino)
        or not grid.esta_livre(inicio)
        or not grid.esta_livre(destino)
    ):
        return ResultadoHPA(
            encontrado=False,
            caminho=[],
            custo=inf,
            nos_expandidos=0,
            nos_expandidos_abstratos=0,
            tempo_segundos=perf_counter() - tempo_inicio,
            quantidade_portais=0,
            tamanho_grafo_abstrato=0,
            quantidade_arestas_abstratas=0,
        )

    if inicio == destino:
        return ResultadoHPA(
            encontrado=True,
            caminho=[inicio],
            custo=0.0,
            nos_expandidos=1,
            nos_expandidos_abstratos=0,
            tempo_segundos=perf_counter() - tempo_inicio,
            quantidade_portais=0,
            tamanho_grafo_abstrato=1,
            quantidade_arestas_abstratas=0,
        )

    clusters = dividir_em_clusters(
        grid=grid,
        tamanho_cluster=tamanho_cluster,
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

    cluster_inicio = encontrar_cluster(
        clusters,
        inicio,
    )

    cluster_destino = encontrar_cluster(
        clusters,
        destino,
    )

    if cluster_inicio is None or cluster_destino is None:
        return ResultadoHPA(
            encontrado=False,
            caminho=[],
            custo=inf,
            nos_expandidos=0,
            nos_expandidos_abstratos=0,
            tempo_segundos=perf_counter() - tempo_inicio,
            quantidade_portais=len(portais),
            tamanho_grafo_abstrato=grafo.quantidade_nos,
            quantidade_arestas_abstratas=grafo.quantidade_arestas,
        )

    no_inicio = NoAbstrato(
        cluster_id=cluster_inicio.identificador,
        posicao=inicio,
    )

    no_destino = NoAbstrato(
        cluster_id=cluster_destino.identificador,
        posicao=destino,
    )

    nos_expandidos_locais = 0

    nos_expandidos_locais += conectar_posicao_ao_cluster(
        grafo=grafo,
        grid=grid,
        cluster=cluster_inicio,
        no_posicao=no_inicio,
    )

    nos_expandidos_locais += conectar_posicao_ao_cluster(
        grafo=grafo,
        grid=grid,
        cluster=cluster_destino,
        no_posicao=no_destino,
    )

    if (
        cluster_inicio.identificador
        == cluster_destino.identificador
    ):
        nos_expandidos_locais += (
            conectar_inicio_ao_destino_no_mesmo_cluster(
                grafo=grafo,
                grid=grid,
                cluster=cluster_inicio,
                no_inicio=no_inicio,
                no_destino=no_destino,
            )
        )

    resultado_abstrato = buscar_no_grafo_abstrato(
        grafo=grafo,
        inicio=no_inicio,
        destino=no_destino,
    )

    if not resultado_abstrato.encontrado:
        return ResultadoHPA(
            encontrado=False,
            caminho=[],
            custo=inf,
            nos_expandidos=(
                nos_expandidos_locais
                + resultado_abstrato.nos_expandidos
            ),
            nos_expandidos_abstratos=(
                resultado_abstrato.nos_expandidos
            ),
            tempo_segundos=perf_counter() - tempo_inicio,
            quantidade_portais=len(portais),
            tamanho_grafo_abstrato=grafo.quantidade_nos,
            quantidade_arestas_abstratas=(
                grafo.quantidade_arestas
            ),
        )

    caminho_completo = montar_caminho_do_grid(
        resultado_abstrato.arestas
    )

    return ResultadoHPA(
        encontrado=True,
        caminho=caminho_completo,
        custo=resultado_abstrato.custo,
        nos_expandidos=(
            nos_expandidos_locais
            + resultado_abstrato.nos_expandidos
        ),
        nos_expandidos_abstratos=(
            resultado_abstrato.nos_expandidos
        ),
        tempo_segundos=perf_counter() - tempo_inicio,
        quantidade_portais=len(portais),
        tamanho_grafo_abstrato=grafo.quantidade_nos,
        quantidade_arestas_abstratas=(
            grafo.quantidade_arestas
        ),
    )