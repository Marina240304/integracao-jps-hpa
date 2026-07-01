import csv
from pathlib import Path


PASTA_PROJETO = Path(__file__).parent

PASTA_SAIDA = (
    PASTA_PROJETO
    / "resultados_consolidados"
)

TAMANHOS_OBRIGATORIOS = {
    256,
    512,
    1024,
}

ORDEM_DENSIDADES = {
    "baixa": 0,
    "media": 1,
    "alta": 2,
}

ORDEM_ALGORITMOS = {
    "A*": 0,
    "JPS": 1,
    "HPA*": 2,
    "HPA-JPS": 3,
}


def localizar_pastas_resultados() -> list[Path]:
    """
    Localiza as pastas resultados_* existentes
    na raiz do projeto.
    """

    pastas = [
        caminho
        for caminho in PASTA_PROJETO.iterdir()
        if (
            caminho.is_dir()
            and caminho.name.startswith(
                "resultados_"
            )
            and caminho.name
            != "resultados_consolidados"
        )
    ]

    return sorted(
        pastas,
        key=lambda caminho: caminho.name,
    )


def ler_csv(
    caminho: Path,
    origem: str,
) -> list[dict]:
    """
    Lê um CSV separado por ponto e vírgula
    e adiciona a pasta de origem.
    """

    if not caminho.exists():
        print(
            f"Arquivo não encontrado: {caminho}"
        )
        return []

    with caminho.open(
        "r",
        newline="",
        encoding="utf-8-sig",
    ) as arquivo:
        leitor = csv.DictReader(
            arquivo,
            delimiter=";",
        )

        linhas = []

        for linha in leitor:
            linha_com_origem = {
                "origem_resultado": origem,
                **linha,
            }

            linhas.append(
                linha_com_origem
            )

    return linhas


def converter_inteiro(
    valor: str,
    padrao: int = 0,
) -> int:
    try:
        return int(float(valor))
    except (
        TypeError,
        ValueError,
    ):
        return padrao


def ordenar_linhas(
    linhas: list[dict],
) -> list[dict]:
    """
    Ordena por tamanho, densidade, algoritmo,
    mapa e repetição.
    """

    return sorted(
        linhas,
        key=lambda linha: (
            converter_inteiro(
                linha.get(
                    "tamanho_mapa",
                    "0",
                )
            ),
            ORDEM_DENSIDADES.get(
                linha.get(
                    "densidade_nome",
                    "",
                ),
                99,
            ),
            ORDEM_ALGORITMOS.get(
                linha.get(
                    "algoritmo",
                    "",
                ),
                99,
            ),
            converter_inteiro(
                linha.get(
                    "numero_mapa",
                    "0",
                )
            ),
            converter_inteiro(
                linha.get(
                    "repeticao",
                    "0",
                )
            ),
        ),
    )


def filtrar_tamanhos_obrigatorios(
    linhas: list[dict],
) -> list[dict]:
    return [
        linha
        for linha in linhas
        if converter_inteiro(
            linha.get(
                "tamanho_mapa",
                "0",
            )
        )
        in TAMANHOS_OBRIGATORIOS
    ]


def salvar_csv(
    linhas: list[dict],
    caminho: Path,
) -> None:
    if not linhas:
        print(
            f"Nenhuma linha para salvar em "
            f"{caminho.name}."
        )
        return

    campos = list(
        linhas[0].keys()
    )

    with caminho.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as arquivo:
        escritor = csv.DictWriter(
            arquivo,
            fieldnames=campos,
            delimiter=";",
        )

        escritor.writeheader()
        escritor.writerows(linhas)


def verificar_quantidades(
    brutos: list[dict],
    resumos: list[dict],
) -> None:
    print(
        "\n===== VERIFICAÇÃO ====="
    )

    print(
        f"Linhas de resultados brutos: "
        f"{len(brutos)}"
    )

    print(
        f"Linhas dos resumos: "
        f"{len(resumos)}"
    )

    tamanhos = sorted(
        {
            converter_inteiro(
                linha["tamanho_mapa"]
            )
            for linha in resumos
        }
    )

    print(
        f"Tamanhos encontrados: {tamanhos}"
    )

    algoritmos = sorted(
        {
            linha["algoritmo"]
            for linha in resumos
        }
    )

    print(
        f"Algoritmos encontrados: "
        f"{algoritmos}"
    )

    densidades = sorted(
        {
            linha["densidade_nome"]
            for linha in resumos
        }
    )

    print(
        f"Densidades encontradas: "
        f"{densidades}"
    )


def main() -> None:
    pastas = localizar_pastas_resultados()

    if not pastas:
        raise RuntimeError(
            "Nenhuma pasta resultados_* "
            "foi encontrada."
        )

    print(
        "===== PASTAS ENCONTRADAS ====="
    )

    for pasta in pastas:
        print(pasta.name)

    resultados_brutos = []
    resumos = []

    for pasta in pastas:
        resultados_brutos.extend(
            ler_csv(
                caminho=(
                    pasta
                    / "resultados_brutos.csv"
                ),
                origem=pasta.name,
            )
        )

        resumos.extend(
            ler_csv(
                caminho=(
                    pasta
                    / "resumo_resultados.csv"
                ),
                origem=pasta.name,
            )
        )

    resultados_brutos = ordenar_linhas(
        resultados_brutos
    )

    resumos = ordenar_linhas(
        resumos
    )

    brutos_obrigatorios = (
        filtrar_tamanhos_obrigatorios(
            resultados_brutos
        )
    )

    resumos_obrigatorios = (
        filtrar_tamanhos_obrigatorios(
            resumos
        )
    )

    PASTA_SAIDA.mkdir(
        exist_ok=True
    )

    salvar_csv(
        linhas=resultados_brutos,
        caminho=(
            PASTA_SAIDA
            / "resultados_brutos_todos.csv"
        ),
    )

    salvar_csv(
        linhas=resumos,
        caminho=(
            PASTA_SAIDA
            / "resumo_todos.csv"
        ),
    )

    salvar_csv(
        linhas=brutos_obrigatorios,
        caminho=(
            PASTA_SAIDA
            / "resultados_brutos_obrigatorios.csv"
        ),
    )

    salvar_csv(
        linhas=resumos_obrigatorios,
        caminho=(
            PASTA_SAIDA
            / "resumo_obrigatorios.csv"
        ),
    )

    verificar_quantidades(
        brutos=resultados_brutos,
        resumos=resumos,
    )

    print(
        "\n===== ARQUIVOS GERADOS ====="
    )

    for caminho in sorted(
        PASTA_SAIDA.iterdir()
    ):
        print(caminho.resolve())


if __name__ == "__main__":
    main()