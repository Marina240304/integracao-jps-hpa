
from dataclasses import dataclass
from itertools import combinations
from math import inf
from time import perf_counter

from src.busca_abstrata import (
    buscar_no_grafo_abstrato,
    montar_caminho_do_grid,
)
from src.grafo_abstrato import (
    GrafoAbstrato,
    NoAbstrato,
    criar_grid_restrito_ao_cluster,
)
from src.grid import Grid, Posicao
from src.hpa import (
    Cluster,
    Portal,
    dividir_em_clusters,
    encontrar_cluster,
    identificar_portais,
)
from src.jps import buscar_caminho_jps


@dataclass(slots=True)
class ResultadoHPAJPS:
    """
    Resultado da integração entre HPA* e JPS.
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
    jump_points_identificados: int


def construir_grafo_abstrato_jps(
    grid: Grid,
    clusters: list[Cluster],
    portais: list[Portal],
) -> tuple[GrafoAbstrato, int, int]:
    """
    Constrói o grafo abstrato do HPA-JPS.

    As conexões entre portais pertencentes ao mesmo
    cluster são calculadas usando JPS.

    Retorna:
    - o grafo abstrato;
    - os nós expandidos no pré-processamento;
    - os Jump Points identificados.
    """

    grafo = GrafoAbstrato()

    nos_por_cluster: dict[
        int,
        set[NoAbstrato],
    ] = {}

    nos_expandidos_preprocessamento = 0
    jump_points = 0

    # Cria os nós dos portais e as conexões que
    # atravessam as fronteiras entre clusters.
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

    # Conecta os portais pertencentes ao mesmo
    # cluster utilizando JPS.
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
            resultado = buscar_caminho_jps(
                grid=grid_restrito,
                inicio=no_origem.posicao,
                destino=no_destino.posicao,
            )

            nos_expandidos_preprocessamento += (
                resultado.nos_expandidos
            )

            jump_points += (
                resultado.jump_points_identificados
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

    return (
        grafo,
        nos_expandidos_preprocessamento,
        jump_points,
    )


def conectar_posicao_ao_cluster_jps(
    grafo: GrafoAbstrato,
    grid: Grid,
    cluster: Cluster,
    no_posicao: NoAbstrato,
) -> tuple[int, int]:
    """
    Conecta a posição inicial ou final aos portais
    pertencentes ao mesmo cluster usando JPS.

    Retorna:
    - a quantidade de nós expandidos;
    - a quantidade de Jump Points identificados.
    """

    grafo.adicionar_no(no_posicao)

    grid_restrito = criar_grid_restrito_ao_cluster(
        grid=grid,
        cluster=cluster,
    )

    nos_expandidos = 0
    jump_points = 0

    nos_do_cluster = [
        no
        for no in list(grafo.adjacencias.keys())
        if (
            no.cluster_id == cluster.identificador
            and no != no_posicao
        )
    ]

    for no_portal in nos_do_cluster:
        resultado = buscar_caminho_jps(
            grid=grid_restrito,
            inicio=no_posicao.posicao,
            destino=no_portal.posicao,
        )

        nos_expandidos += resultado.nos_expandidos

        jump_points += (
            resultado.jump_points_identificados
        )

        if not resultado.encontrado:
            continue

        grafo.adicionar_aresta_bidirecional(
            origem=no_posicao,
            destino=no_portal,
            custo=resultado.custo,
            caminho=resultado.caminho,
            tipo="conexao_consulta",
        )

    return nos_expandidos, jump_points


def conectar_inicio_destino_mesmo_cluster_jps(
    grafo: GrafoAbstrato,
    grid: Grid,
    cluster: Cluster,
    no_inicio: NoAbstrato,
    no_destino: NoAbstrato,
) -> tuple[int, int]:
    """
    Cria uma conexão direta usando JPS quando início
    e destino pertencem ao mesmo cluster.
    """

    grid_restrito = criar_grid_restrito_ao_cluster(
        grid=grid,
        cluster=cluster,
    )

    resultado = buscar_caminho_jps(
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

    return (
        resultado.nos_expandidos,
        resultado.jump_points_identificados,
    )


def criar_resultado_sem_caminho(
    tempo_inicio: float,
    quantidade_portais: int = 0,
    tamanho_grafo_abstrato: int = 0,
    quantidade_arestas_abstratas: int = 0,
    nos_expandidos: int = 0,
    nos_expandidos_abstratos: int = 0,
    jump_points: int = 0,
) -> ResultadoHPAJPS:
    """
    Cria um resultado padronizado para casos em que
    nenhum caminho foi encontrado.
    """

    return ResultadoHPAJPS(
        encontrado=False,
        caminho=[],
        custo=inf,
        nos_expandidos=nos_expandidos,
        nos_expandidos_abstratos=(
            nos_expandidos_abstratos
        ),
        tempo_segundos=perf_counter() - tempo_inicio,
        quantidade_portais=quantidade_portais,
        tamanho_grafo_abstrato=tamanho_grafo_abstrato,
        quantidade_arestas_abstratas=(
            quantidade_arestas_abstratas
        ),
        jump_points_identificados=jump_points,
    )


def buscar_hpa_jps(
    grid: Grid,
    inicio: Posicao,
    destino: Posicao,
    tamanho_cluster: int,
) -> ResultadoHPAJPS:
    """
    Executa a integração entre HPA* e JPS.

    Etapas:
    1. Divide o mapa em clusters;
    2. Identifica os portais;
    3. Constrói o grafo abstrato;
    4. Usa JPS nas buscas locais;
    5. Executa A* no grafo abstrato;
    6. Reconstrói o caminho completo.

    A métrica de nós expandidos considera a fase de
    consulta, assim como na implementação do HPA*
    tradicional. As expansões do pré-processamento do
    grafo abstrato não são somadas nessa métrica.
    """

    tempo_inicio = perf_counter()

    if tamanho_cluster <= 0:
        raise ValueError(
            "O tamanho do cluster deve ser maior que zero."
        )

    if (
        not grid.esta_dentro(inicio)
        or not grid.esta_dentro(destino)
        or not grid.esta_livre(inicio)
        or not grid.esta_livre(destino)
    ):
        return criar_resultado_sem_caminho(
            tempo_inicio=tempo_inicio,
        )

    if inicio == destino:
        return ResultadoHPAJPS(
            encontrado=True,
            caminho=[inicio],
            custo=0.0,
            nos_expandidos=1,
            nos_expandidos_abstratos=0,
            tempo_segundos=perf_counter() - tempo_inicio,
            quantidade_portais=0,
            tamanho_grafo_abstrato=1,
            quantidade_arestas_abstratas=0,
            jump_points_identificados=0,
        )

    clusters = dividir_em_clusters(
        grid=grid,
        tamanho_cluster=tamanho_cluster,
    )

    portais = identificar_portais(
        grid=grid,
        clusters=clusters,
    )

    (
        grafo,
        _nos_expandidos_preprocessamento,
        jump_points,
    ) = construir_grafo_abstrato_jps(
        grid=grid,
        clusters=clusters,
        portais=portais,
    )

    # A contagem da consulta começa após a construção
    # do grafo abstrato, seguindo a mesma metodologia
    # usada no HPA* tradicional.
    nos_expandidos = 0

    cluster_inicio = encontrar_cluster(
        clusters,
        inicio,
    )

    cluster_destino = encontrar_cluster(
        clusters,
        destino,
    )

    if cluster_inicio is None or cluster_destino is None:
        return criar_resultado_sem_caminho(
            tempo_inicio=tempo_inicio,
            quantidade_portais=len(portais),
            tamanho_grafo_abstrato=(
                grafo.quantidade_nos
            ),
            quantidade_arestas_abstratas=(
                grafo.quantidade_arestas
            ),
            nos_expandidos=nos_expandidos,
            jump_points=jump_points,
        )

    no_inicio = NoAbstrato(
        cluster_id=cluster_inicio.identificador,
        posicao=inicio,
    )

    no_destino = NoAbstrato(
        cluster_id=cluster_destino.identificador,
        posicao=destino,
    )

    (
        expandidos_inicio,
        jump_points_inicio,
    ) = conectar_posicao_ao_cluster_jps(
        grafo=grafo,
        grid=grid,
        cluster=cluster_inicio,
        no_posicao=no_inicio,
    )

    nos_expandidos += expandidos_inicio
    jump_points += jump_points_inicio

    (
        expandidos_destino,
        jump_points_destino,
    ) = conectar_posicao_ao_cluster_jps(
        grafo=grafo,
        grid=grid,
        cluster=cluster_destino,
        no_posicao=no_destino,
    )

    nos_expandidos += expandidos_destino
    jump_points += jump_points_destino

    if (
        cluster_inicio.identificador
        == cluster_destino.identificador
    ):
        (
            expandidos_diretos,
            jump_points_diretos,
        ) = conectar_inicio_destino_mesmo_cluster_jps(
            grafo=grafo,
            grid=grid,
            cluster=cluster_inicio,
            no_inicio=no_inicio,
            no_destino=no_destino,
        )

        nos_expandidos += expandidos_diretos
        jump_points += jump_points_diretos

    resultado_abstrato = buscar_no_grafo_abstrato(
        grafo=grafo,
        inicio=no_inicio,
        destino=no_destino,
    )

    nos_expandidos += (
        resultado_abstrato.nos_expandidos
    )

    if not resultado_abstrato.encontrado:
        return criar_resultado_sem_caminho(
            tempo_inicio=tempo_inicio,
            quantidade_portais=len(portais),
            tamanho_grafo_abstrato=(
                grafo.quantidade_nos
            ),
            quantidade_arestas_abstratas=(
                grafo.quantidade_arestas
            ),
            nos_expandidos=nos_expandidos,
            nos_expandidos_abstratos=(
                resultado_abstrato.nos_expandidos
            ),
            jump_points=jump_points,
        )

    caminho_completo = montar_caminho_do_grid(
        resultado_abstrato.arestas
    )

    return ResultadoHPAJPS(
        encontrado=True,
        caminho=caminho_completo,
        custo=resultado_abstrato.custo,
        nos_expandidos=nos_expandidos,
        nos_expandidos_abstratos=(
            resultado_abstrato.nos_expandidos
        ),
        tempo_segundos=perf_counter() - tempo_inicio,
        quantidade_portais=len(portais),
        tamanho_grafo_abstrato=(
            grafo.quantidade_nos
        ),
        quantidade_arestas_abstratas=(
            grafo.quantidade_arestas
        ),
        jump_points_identificados=jump_points,
    )

