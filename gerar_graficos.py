import csv
from pathlib import Path

import matplotlib.pyplot as plt


PASTA_PROJETO = Path(__file__).parent

ARQUIVO_RESULTADOS = (
    PASTA_PROJETO
    / "resultados_consolidados"
    / "resumo_obrigatorios.csv"
)

PASTA_GRAFICOS = (
    PASTA_PROJETO
    / "graficos"
)

TAMANHOS = [256, 512, 1024]

DENSIDADES = [
    "baixa",
    "media",
    "alta",
]

ALGORITMOS = [
    "A*",
    "JPS",
    "HPA*",
    "HPA-JPS",
]


def converter_float(valor: str) -> float:
    if valor is None or valor == "":
        return 0.0

    return float(valor.replace(",", "."))


def carregar_resultados() -> list[dict]:
    if not ARQUIVO_RESULTADOS.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {ARQUIVO_RESULTADOS}"
        )

    with ARQUIVO_RESULTADOS.open(
        "r",
        newline="",
        encoding="utf-8-sig",
    ) as arquivo:
        leitor = csv.DictReader(
            arquivo,
            delimiter=";",
        )

        resultados = []

        for linha in leitor:
            linha["tamanho_mapa"] = int(
                float(linha["tamanho_mapa"])
            )

            campos_numericos = [
                "tempo_medio_segundos",
                "desvio_tempo_segundos",
                "nos_expandidos_medios",
                "custo_medio",
                "passos_medios",
                "portais_medios",
                "jump_points_medios",
                "nos_abstratos_medios",
            ]

            for campo in campos_numericos:
                linha[campo] = converter_float(
                    linha.get(campo, "")
                )

            resultados.append(linha)

    return resultados


def encontrar_resultado(
    resultados: list[dict],
    tamanho: int,
    densidade: str,
    algoritmo: str,
) -> dict:
    for linha in resultados:
        if (
            linha["tamanho_mapa"] == tamanho
            and linha["densidade_nome"] == densidade
            and linha["algoritmo"] == algoritmo
        ):
            return linha

    raise ValueError(
        f"Resultado ausente: mapa {tamanho}, "
        f"densidade {densidade}, algoritmo {algoritmo}."
    )


def verificar_resultados(
    resultados: list[dict],
) -> None:
    quantidade_esperada = (
        len(TAMANHOS)
        * len(DENSIDADES)
        * len(ALGORITMOS)
    )

    if len(resultados) != quantidade_esperada:
        raise ValueError(
            f"Esperadas {quantidade_esperada} linhas, "
            f"mas foram encontradas {len(resultados)}."
        )

    for tamanho in TAMANHOS:
        for densidade in DENSIDADES:
            for algoritmo in ALGORITMOS:
                encontrar_resultado(
                    resultados=resultados,
                    tamanho=tamanho,
                    densidade=densidade,
                    algoritmo=algoritmo,
                )


def salvar_figura(
    nome_arquivo: str,
) -> None:
    caminho = PASTA_GRAFICOS / nome_arquivo

    plt.tight_layout()

    plt.savefig(
        caminho,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()

    print(f"Gráfico salvo: {caminho}")


def gerar_graficos_por_densidade(
    resultados: list[dict],
    campo: str,
    titulo_base: str,
    rotulo_y: str,
    prefixo_arquivo: str,
    escala_logaritmica: bool,
) -> None:
    for densidade in DENSIDADES:
        plt.figure(figsize=(8, 5))

        for algoritmo in ALGORITMOS:
            valores = []

            for tamanho in TAMANHOS:
                linha = encontrar_resultado(
                    resultados=resultados,
                    tamanho=tamanho,
                    densidade=densidade,
                    algoritmo=algoritmo,
                )

                valores.append(
                    linha[campo]
                )

            plt.plot(
                TAMANHOS,
                valores,
                marker="o",
                label=algoritmo,
            )

        if escala_logaritmica:
            plt.yscale("log")

        plt.title(
            f"{titulo_base} — densidade {densidade}"
        )

        plt.xlabel("Dimensão do mapa")
        plt.ylabel(rotulo_y)

        plt.xticks(
            TAMANHOS,
            [f"{t} × {t}" for t in TAMANHOS],
        )

        plt.grid(
            True,
            linestyle="--",
            alpha=0.4,
        )

        plt.legend()

        salvar_figura(
            f"{prefixo_arquivo}_{densidade}.png"
        )


def calcular_reducao_percentual(
    valor_referencia: float,
    valor_novo: float,
) -> float:
    if valor_referencia == 0:
        return 0.0

    return (
        (valor_referencia - valor_novo)
        / valor_referencia
        * 100.0
    )


def gerar_grafico_reducao_hpa_jps(
    resultados: list[dict],
) -> None:
    plt.figure(figsize=(8, 5))

    for densidade in DENSIDADES:
        reducoes = []

        for tamanho in TAMANHOS:
            hpa = encontrar_resultado(
                resultados=resultados,
                tamanho=tamanho,
                densidade=densidade,
                algoritmo="HPA*",
            )

            hpa_jps = encontrar_resultado(
                resultados=resultados,
                tamanho=tamanho,
                densidade=densidade,
                algoritmo="HPA-JPS",
            )

            reducao = calcular_reducao_percentual(
                valor_referencia=(
                    hpa["nos_expandidos_medios"]
                ),
                valor_novo=(
                    hpa_jps["nos_expandidos_medios"]
                ),
            )

            reducoes.append(reducao)

        plt.plot(
            TAMANHOS,
            reducoes,
            marker="o",
            label=densidade,
        )

    plt.axhline(
        y=0,
        linewidth=1,
    )

    plt.title(
        "Redução de nós expandidos do HPA-JPS "
        "em relação ao HPA*"
    )

    plt.xlabel("Dimensão do mapa")
    plt.ylabel("Redução de nós expandidos (%)")

    plt.xticks(
        TAMANHOS,
        [f"{t} × {t}" for t in TAMANHOS],
    )

    plt.grid(
        True,
        linestyle="--",
        alpha=0.4,
    )

    plt.legend(title="Densidade")

    salvar_figura(
        "reducao_nos_hpa_jps.png"
    )


def gerar_grafico_grafo_abstrato(
    resultados: list[dict],
) -> None:
    plt.figure(figsize=(8, 5))

    for densidade in DENSIDADES:
        quantidades = []

        for tamanho in TAMANHOS:
            linha = encontrar_resultado(
                resultados=resultados,
                tamanho=tamanho,
                densidade=densidade,
                algoritmo="HPA*",
            )

            quantidades.append(
                linha["nos_abstratos_medios"]
            )

        plt.plot(
            TAMANHOS,
            quantidades,
            marker="o",
            label=densidade,
        )

    plt.yscale("log")

    plt.title(
        "Tamanho do grafo abstrato"
    )

    plt.xlabel("Dimensão do mapa")
    plt.ylabel("Quantidade de nós abstratos")

    plt.xticks(
        TAMANHOS,
        [f"{t} × {t}" for t in TAMANHOS],
    )

    plt.grid(
        True,
        linestyle="--",
        alpha=0.4,
    )

    plt.legend(title="Densidade")

    salvar_figura(
        "tamanho_grafo_abstrato.png"
    )


def gerar_grafico_portais(
    resultados: list[dict],
) -> None:
    plt.figure(figsize=(8, 5))

    for densidade in DENSIDADES:
        quantidades = []

        for tamanho in TAMANHOS:
            linha = encontrar_resultado(
                resultados=resultados,
                tamanho=tamanho,
                densidade=densidade,
                algoritmo="HPA*",
            )

            quantidades.append(
                linha["portais_medios"]
            )

        plt.plot(
            TAMANHOS,
            quantidades,
            marker="o",
            label=densidade,
        )

    plt.yscale("log")

    plt.title(
        "Quantidade de portais do HPA*"
    )

    plt.xlabel("Dimensão do mapa")
    plt.ylabel("Quantidade de portais")

    plt.xticks(
        TAMANHOS,
        [f"{t} × {t}" for t in TAMANHOS],
    )

    plt.grid(
        True,
        linestyle="--",
        alpha=0.4,
    )

    plt.legend(title="Densidade")

    salvar_figura(
        "quantidade_portais.png"
    )


def salvar_tabela_reducoes(
    resultados: list[dict],
) -> None:
    caminho = (
        PASTA_GRAFICOS
        / "reducoes_hpa_jps.csv"
    )

    linhas = []

    for tamanho in TAMANHOS:
        for densidade in DENSIDADES:
            hpa = encontrar_resultado(
                resultados=resultados,
                tamanho=tamanho,
                densidade=densidade,
                algoritmo="HPA*",
            )

            hpa_jps = encontrar_resultado(
                resultados=resultados,
                tamanho=tamanho,
                densidade=densidade,
                algoritmo="HPA-JPS",
            )

            reducao_expansoes = calcular_reducao_percentual(
                hpa["nos_expandidos_medios"],
                hpa_jps["nos_expandidos_medios"],
            )

            variacao_tempo = (
                (
                    hpa_jps["tempo_medio_segundos"]
                    - hpa["tempo_medio_segundos"]
                )
                / hpa["tempo_medio_segundos"]
                * 100.0
            )

            linhas.append(
                {
                    "tamanho_mapa": tamanho,
                    "densidade": densidade,
                    "nos_hpa": (
                        hpa["nos_expandidos_medios"]
                    ),
                    "nos_hpa_jps": (
                        hpa_jps[
                            "nos_expandidos_medios"
                        ]
                    ),
                    "reducao_nos_percentual": (
                        reducao_expansoes
                    ),
                    "tempo_hpa_segundos": (
                        hpa["tempo_medio_segundos"]
                    ),
                    "tempo_hpa_jps_segundos": (
                        hpa_jps[
                            "tempo_medio_segundos"
                        ]
                    ),
                    "variacao_tempo_percentual": (
                        variacao_tempo
                    ),
                }
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

    print(f"Tabela salva: {caminho}")


def main() -> None:
    PASTA_GRAFICOS.mkdir(
        exist_ok=True
    )

    resultados = carregar_resultados()

    verificar_resultados(
        resultados
    )

    gerar_graficos_por_densidade(
        resultados=resultados,
        campo="tempo_medio_segundos",
        titulo_base="Tempo total de execução",
        rotulo_y="Tempo (segundos, escala logarítmica)",
        prefixo_arquivo="tempo_execucao",
        escala_logaritmica=True,
    )

    gerar_graficos_por_densidade(
        resultados=resultados,
        campo="nos_expandidos_medios",
        titulo_base="Nós expandidos",
        rotulo_y="Nós expandidos (escala logarítmica)",
        prefixo_arquivo="nos_expandidos",
        escala_logaritmica=True,
    )

    gerar_graficos_por_densidade(
        resultados=resultados,
        campo="custo_medio",
        titulo_base="Custo do caminho encontrado",
        rotulo_y="Custo total do caminho",
        prefixo_arquivo="custo_caminho",
        escala_logaritmica=False,
    )

    gerar_grafico_reducao_hpa_jps(
        resultados
    )

    gerar_grafico_grafo_abstrato(
        resultados
    )

    gerar_grafico_portais(
        resultados
    )

    salvar_tabela_reducoes(
        resultados
    )

    print(
        "\nTodos os gráficos foram gerados em:"
    )

    print(PASTA_GRAFICOS.resolve())


if __name__ == "__main__":
    main()