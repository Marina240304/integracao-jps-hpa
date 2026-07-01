import csv
from collections import defaultdict
from pathlib import Path
from random import Random
from statistics import mean, stdev

from src.astar import buscar_caminho
from src.grid import Grid
from src.hpa_busca import buscar_hpa
from src.hpa_jps import buscar_hpa_jps
from src.jps import buscar_caminho_jps


# Configuração inicial para verificar se o programa
# funciona corretamente antes dos experimentos grandes.
TAMANHOS = [1024]

DENSIDADES = {
    "alta": 0.30,
}

REPETICOES = 1
MAPAS_POR_CENARIO = 1
SEMENTE_BASE = 2026

PASTA_RESULTADOS = Path("resultados")
PASTA_MAPAS = PASTA_RESULTADOS / "mapas"


def tamanho_cluster_para_mapa(
    tamanho_mapa: int,
) -> int:
    """
    Define o tamanho dos clusters nos testes iniciais.
    """

    if tamanho_mapa <= 64:
        return 8

    return 16


def calcular_densidade_real(
    grid: Grid,
) -> float:
    quantidade_obstaculos = sum(
        1
        for linha in grid.celulas
        for valor in linha
        if valor == 1
    )

    total_celulas = (
        grid.quantidade_linhas
        * grid.quantidade_colunas
    )

    return quantidade_obstaculos / total_celulas


def liberar_regiao_inicial_e_final(
    matriz: list[list[int]],
    tamanho: int,
) -> None:
    """
    Evita que o início e o destino fiquem imediatamente
    presos por obstáculos.
    """

    posicoes_livres = [
        (tamanho - 1, 0),
        (tamanho - 2, 0),
        (tamanho - 1, 1),
        (0, tamanho - 1),
        (1, tamanho - 1),
        (0, tamanho - 2),
    ]

    for linha, coluna in posicoes_livres:
        if (
            0 <= linha < tamanho
            and 0 <= coluna < tamanho
        ):
            matriz[linha][coluna] = 0


def gerar_mapa_com_caminho(
    tamanho: int,
    densidade: float,
    semente: int,
    maximo_tentativas: int = 100,
) -> tuple[
    Grid,
    tuple[int, int],
    tuple[int, int],
    int,
]:
    """
    Gera um mapa aleatório e verifica com A* se existe
    caminho entre o início e o destino.

    A geração é reproduzível porque utiliza uma
    semente fixa.
    """

    gerador = Random(semente)

    inicio = (tamanho - 1, 0)
    destino = (0, tamanho - 1)

    for tentativa in range(1, maximo_tentativas + 1):
        matriz = [
            [
                1 if gerador.random() < densidade else 0
                for _ in range(tamanho)
            ]
            for _ in range(tamanho)
        ]

        liberar_regiao_inicial_e_final(
            matriz=matriz,
            tamanho=tamanho,
        )

        grid = Grid.criar(matriz)

        validacao = buscar_caminho(
            grid=grid,
            inicio=inicio,
            destino=destino,
        )

        if validacao.encontrado:
            return (
                grid,
                inicio,
                destino,
                tentativa,
            )

    raise RuntimeError(
        f"Não foi possível gerar um mapa {tamanho} x "
        f"{tamanho} com caminho após "
        f"{maximo_tentativas} tentativas."
    )


def salvar_mapa(
    grid: Grid,
    caminho_arquivo: Path,
) -> None:
    """
    Salva o mapa utilizado no experimento.

    0 = célula livre
    1 = obstáculo
    """

    with caminho_arquivo.open(
        "w",
        encoding="utf-8",
    ) as arquivo:
        for linha in grid.celulas:
            arquivo.write(
                "".join(str(valor) for valor in linha)
                + "\n"
            )


def executar_algoritmo(
    nome_algoritmo: str,
    grid: Grid,
    inicio: tuple[int, int],
    destino: tuple[int, int],
    tamanho_cluster: int,
):
    if nome_algoritmo == "A*":
        return buscar_caminho(
            grid=grid,
            inicio=inicio,
            destino=destino,
        )

    if nome_algoritmo == "JPS":
        return buscar_caminho_jps(
            grid=grid,
            inicio=inicio,
            destino=destino,
        )

    if nome_algoritmo == "HPA*":
        return buscar_hpa(
            grid=grid,
            inicio=inicio,
            destino=destino,
            tamanho_cluster=tamanho_cluster,
        )

    if nome_algoritmo == "HPA-JPS":
        return buscar_hpa_jps(
            grid=grid,
            inicio=inicio,
            destino=destino,
            tamanho_cluster=tamanho_cluster,
        )

    raise ValueError(
        f"Algoritmo desconhecido: {nome_algoritmo}"
    )


def transformar_resultado_em_linha(
    nome_algoritmo: str,
    resultado,
    tamanho: int,
    tamanho_cluster: int,
    densidade_nome: str,
    densidade_configurada: float,
    densidade_real: float,
    semente: int,
    numero_mapa: int,
    repeticao: int,
    tentativa_mapa: int,
) -> dict:
    encontrado = resultado.encontrado

    if encontrado:
        custo = resultado.custo
        passos = max(
            0,
            len(resultado.caminho) - 1,
        )
        quantidade_posicoes = len(
            resultado.caminho
        )
    else:
        custo = ""
        passos = ""
        quantidade_posicoes = ""

    return {
        "algoritmo": nome_algoritmo,
        "tamanho_mapa": tamanho,
        "tamanho_cluster": tamanho_cluster,
        "densidade_nome": densidade_nome,
        "densidade_configurada": (
            densidade_configurada
        ),
        "densidade_real": densidade_real,
        "semente": semente,
        "numero_mapa": numero_mapa,
        "tentativa_geracao_mapa": tentativa_mapa,
        "repeticao": repeticao,
        "encontrado": encontrado,
        "tempo_segundos": resultado.tempo_segundos,
        "nos_expandidos": resultado.nos_expandidos,
        "custo_total": custo,
        "passos_caminho": passos,
        "posicoes_caminho": quantidade_posicoes,
        "nos_expandidos_abstratos": getattr(
            resultado,
            "nos_expandidos_abstratos",
            0,
        ),
        "quantidade_portais": getattr(
            resultado,
            "quantidade_portais",
            0,
        ),
        "jump_points": getattr(
            resultado,
            "jump_points_identificados",
            0,
        ),
        "nos_grafo_abstrato": getattr(
            resultado,
            "tamanho_grafo_abstrato",
            0,
        ),
        "arestas_grafo_abstrato": getattr(
            resultado,
            "quantidade_arestas_abstratas",
            0,
        ),
        "erro": "",
    }


def criar_linha_de_erro(
    nome_algoritmo: str,
    erro: Exception,
    tamanho: int,
    tamanho_cluster: int,
    densidade_nome: str,
    densidade_configurada: float,
    densidade_real: float,
    semente: int,
    numero_mapa: int,
    repeticao: int,
    tentativa_mapa: int,
) -> dict:
    return {
        "algoritmo": nome_algoritmo,
        "tamanho_mapa": tamanho,
        "tamanho_cluster": tamanho_cluster,
        "densidade_nome": densidade_nome,
        "densidade_configurada": (
            densidade_configurada
        ),
        "densidade_real": densidade_real,
        "semente": semente,
        "numero_mapa": numero_mapa,
        "tentativa_geracao_mapa": tentativa_mapa,
        "repeticao": repeticao,
        "encontrado": False,
        "tempo_segundos": "",
        "nos_expandidos": "",
        "custo_total": "",
        "passos_caminho": "",
        "posicoes_caminho": "",
        "nos_expandidos_abstratos": "",
        "quantidade_portais": "",
        "jump_points": "",
        "nos_grafo_abstrato": "",
        "arestas_grafo_abstrato": "",
        "erro": str(erro),
    }


def salvar_resultados_brutos(
    linhas: list[dict],
) -> Path:
    caminho = (
        PASTA_RESULTADOS
        / "resultados_brutos.csv"
    )

    with caminho.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as arquivo:
        escritor = csv.DictWriter(
            arquivo,
            fieldnames=list(linhas[0].keys()),
            delimiter=";",
        )

        escritor.writeheader()
        escritor.writerows(linhas)

    return caminho


def media_segura(
    valores: list[float],
):
    if not valores:
        return ""

    return mean(valores)


def desvio_seguro(
    valores: list[float],
):
    if len(valores) < 2:
        return 0.0

    return stdev(valores)


def criar_resumo(
    linhas: list[dict],
) -> list[dict]:
    grupos = defaultdict(list)

    for linha in linhas:
        chave = (
            linha["tamanho_mapa"],
            linha["densidade_nome"],
            linha["algoritmo"],
        )

        grupos[chave].append(linha)

    resumo = []

    for (
        tamanho,
        densidade_nome,
        algoritmo,
    ), linhas_grupo in grupos.items():
        sucessos = [
            linha
            for linha in linhas_grupo
            if linha["encontrado"] is True
        ]

        tempos = [
            float(linha["tempo_segundos"])
            for linha in sucessos
        ]

        expandidos = [
            float(linha["nos_expandidos"])
            for linha in sucessos
        ]

        custos = [
            float(linha["custo_total"])
            for linha in sucessos
        ]

        passos = [
            float(linha["passos_caminho"])
            for linha in sucessos
        ]

        portais = [
            float(linha["quantidade_portais"])
            for linha in sucessos
        ]

        jump_points = [
            float(linha["jump_points"])
            for linha in sucessos
        ]

        nos_abstratos = [
            float(linha["nos_grafo_abstrato"])
            for linha in sucessos
        ]

        resumo.append(
            {
                "tamanho_mapa": tamanho,
                "densidade_nome": densidade_nome,
                "algoritmo": algoritmo,
                "execucoes": len(linhas_grupo),
                "sucessos": len(sucessos),
                "taxa_sucesso": (
                    len(sucessos)
                    / len(linhas_grupo)
                ),
                "tempo_medio_segundos": (
                    media_segura(tempos)
                ),
                "desvio_tempo_segundos": (
                    desvio_seguro(tempos)
                ),
                "nos_expandidos_medios": (
                    media_segura(expandidos)
                ),
                "custo_medio": (
                    media_segura(custos)
                ),
                "passos_medios": (
                    media_segura(passos)
                ),
                "portais_medios": (
                    media_segura(portais)
                ),
                "jump_points_medios": (
                    media_segura(jump_points)
                ),
                "nos_abstratos_medios": (
                    media_segura(nos_abstratos)
                ),
            }
        )

    resumo.sort(
        key=lambda linha: (
            linha["tamanho_mapa"],
            linha["densidade_nome"],
            linha["algoritmo"],
        )
    )

    return resumo


def salvar_resumo(
    resumo: list[dict],
) -> Path:
    caminho = (
        PASTA_RESULTADOS
        / "resumo_resultados.csv"
    )

    with caminho.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as arquivo:
        escritor = csv.DictWriter(
            arquivo,
            fieldnames=list(resumo[0].keys()),
            delimiter=";",
        )

        escritor.writeheader()
        escritor.writerows(resumo)

    return caminho


def mostrar_resumo_no_terminal(
    resumo: list[dict],
) -> None:
    print("\n===== RESUMO DOS EXPERIMENTOS =====")

    print(
        f"{'Mapa':<10}"
        f"{'Densidade':<12}"
        f"{'Algoritmo':<12}"
        f"{'Sucessos':<12}"
        f"{'Tempo médio':<16}"
        f"{'Expandidos':<14}"
    )

    print("-" * 76)

    for linha in resumo:
        tempo = linha["tempo_medio_segundos"]
        expandidos = linha[
            "nos_expandidos_medios"
        ]

        tempo_texto = (
            f"{tempo:.8f}"
            if tempo != ""
            else "-"
        )

        expandidos_texto = (
            f"{expandidos:.2f}"
            if expandidos != ""
            else "-"
        )

        sucessos = (
            f"{linha['sucessos']}/"
            f"{linha['execucoes']}"
        )

        print(
            f"{linha['tamanho_mapa']:<10}"
            f"{linha['densidade_nome']:<12}"
            f"{linha['algoritmo']:<12}"
            f"{sucessos:<12}"
            f"{tempo_texto:<16}"
            f"{expandidos_texto:<14}"
        )


def main() -> None:
    PASTA_RESULTADOS.mkdir(
        exist_ok=True
    )

    PASTA_MAPAS.mkdir(
        exist_ok=True
    )

    algoritmos = [
        "A*",
        "JPS",
        "HPA*",
        "HPA-JPS",
    ]

    linhas_resultados = []

    total_cenarios = (
        len(TAMANHOS)
        * len(DENSIDADES)
        * MAPAS_POR_CENARIO
    )

    numero_cenario = 0

    for tamanho in TAMANHOS:
        tamanho_cluster = (
            tamanho_cluster_para_mapa(tamanho)
        )

        for indice_densidade, (
            densidade_nome,
            densidade_valor,
        ) in enumerate(DENSIDADES.items()):
            for numero_mapa in range(
                1,
                MAPAS_POR_CENARIO + 1,
            ):
                numero_cenario += 1

                semente = (
                    SEMENTE_BASE
                    + tamanho * 100
                    + indice_densidade * 10
                    + numero_mapa
                )

                print(
                    "\n"
                    f"===== CENÁRIO "
                    f"{numero_cenario}/"
                    f"{total_cenarios} ====="
                )

                print(
                    f"Mapa: {tamanho} x {tamanho}"
                )

                print(
                    f"Densidade: {densidade_nome} "
                    f"({densidade_valor:.0%})"
                )

                print(
                    f"Cluster: "
                    f"{tamanho_cluster} x "
                    f"{tamanho_cluster}"
                )

                print(f"Semente: {semente}")

                (
                    grid,
                    inicio,
                    destino,
                    tentativa_mapa,
                ) = gerar_mapa_com_caminho(
                    tamanho=tamanho,
                    densidade=densidade_valor,
                    semente=semente,
                )

                densidade_real = (
                    calcular_densidade_real(grid)
                )

                print(
                    f"Densidade real: "
                    f"{densidade_real:.2%}"
                )

                print(
                    f"Tentativas para gerar mapa: "
                    f"{tentativa_mapa}"
                )

                nome_mapa = (
                    f"mapa_{tamanho}_"
                    f"{densidade_nome}_"
                    f"semente_{semente}.txt"
                )

                salvar_mapa(
                    grid=grid,
                    caminho_arquivo=(
                        PASTA_MAPAS / nome_mapa
                    ),
                )

                for repeticao in range(
                    1,
                    REPETICOES + 1,
                ):
                    for algoritmo in algoritmos:
                        print(
                            f"Executando {algoritmo} — "
                            f"repetição "
                            f"{repeticao}/"
                            f"{REPETICOES}"
                        )

                        try:
                            resultado = (
                                executar_algoritmo(
                                    nome_algoritmo=algoritmo,
                                    grid=grid,
                                    inicio=inicio,
                                    destino=destino,
                                    tamanho_cluster=(
                                        tamanho_cluster
                                    ),
                                )
                            )

                            linha = (
                                transformar_resultado_em_linha(
                                    nome_algoritmo=algoritmo,
                                    resultado=resultado,
                                    tamanho=tamanho,
                                    tamanho_cluster=(
                                        tamanho_cluster
                                    ),
                                    densidade_nome=(
                                        densidade_nome
                                    ),
                                    densidade_configurada=(
                                        densidade_valor
                                    ),
                                    densidade_real=(
                                        densidade_real
                                    ),
                                    semente=semente,
                                    numero_mapa=numero_mapa,
                                    repeticao=repeticao,
                                    tentativa_mapa=(
                                        tentativa_mapa
                                    ),
                                )
                            )

                        except Exception as erro:
                            print(
                                f"Erro em {algoritmo}: "
                                f"{erro}"
                            )

                            linha = criar_linha_de_erro(
                                nome_algoritmo=algoritmo,
                                erro=erro,
                                tamanho=tamanho,
                                tamanho_cluster=(
                                    tamanho_cluster
                                ),
                                densidade_nome=(
                                    densidade_nome
                                ),
                                densidade_configurada=(
                                    densidade_valor
                                ),
                                densidade_real=(
                                    densidade_real
                                ),
                                semente=semente,
                                numero_mapa=numero_mapa,
                                repeticao=repeticao,
                                tentativa_mapa=(
                                    tentativa_mapa
                                ),
                            )

                        linhas_resultados.append(linha)

    caminho_brutos = salvar_resultados_brutos(
        linhas_resultados
    )

    resumo = criar_resumo(
        linhas_resultados
    )

    caminho_resumo = salvar_resumo(
        resumo
    )

    mostrar_resumo_no_terminal(
        resumo
    )

    print(
        "\nResultados brutos salvos em:"
    )
    print(caminho_brutos.resolve())

    print(
        "\nResumo salvo em:"
    )
    print(caminho_resumo.resolve())

    print(
        "\nMapas utilizados salvos em:"
    )
    print(PASTA_MAPAS.resolve())


if __name__ == "__main__":
    main()