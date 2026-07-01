import csv
from collections import defaultdict
from math import isclose
from pathlib import Path


ARQUIVO = (
    Path(__file__).parent
    / "resultados_consolidados"
    / "resultados_brutos_obrigatorios.csv"
)


def converter_float(valor: str) -> float | None:
    if valor is None or valor == "":
        return None

    return float(valor.replace(",", "."))


def main() -> None:
    with ARQUIVO.open(
        "r",
        newline="",
        encoding="utf-8-sig",
    ) as arquivo:
        linhas = list(
            csv.DictReader(
                arquivo,
                delimiter=";",
            )
        )

    grupos = defaultdict(list)

    for linha in linhas:
        chave = (
            linha["tamanho_mapa"],
            linha["densidade_nome"],
            linha["numero_mapa"],
            linha["repeticao"],
        )

        grupos[chave].append(linha)

    problemas = 0

    print("===== VERIFICAÇÃO DOS RESULTADOS =====")

    for chave, resultados in sorted(grupos.items()):
        tamanho, densidade, mapa, repeticao = chave

        custos = {
            linha["algoritmo"]: converter_float(
                linha["custo_total"]
            )
            for linha in resultados
        }

        encontrados = {
            linha["algoritmo"]: (
                linha["encontrado"].lower() == "true"
            )
            for linha in resultados
        }

        todos_encontraram = all(
            encontrados.values()
        )

        custos_validos = [
            custo
            for custo in custos.values()
            if custo is not None
        ]

        custos_iguais = (
            len(custos_validos) == 4
            and all(
                isclose(
                    custo,
                    custos_validos[0],
                    rel_tol=1e-9,
                    abs_tol=1e-9,
                )
                for custo in custos_validos
            )
        )

        situacao = (
            "OK"
            if todos_encontraram and custos_iguais
            else "PROBLEMA"
        )

        print(
            f"{tamanho} × {tamanho} | "
            f"{densidade:<5} | "
            f"{situacao}"
        )

        if situacao == "PROBLEMA":
            problemas += 1
            print(f"  Encontrados: {encontrados}")
            print(f"  Custos: {custos}")

    print()

    if problemas == 0:
        print(
            "Todos os algoritmos encontraram caminhos "
            "com o mesmo custo em todos os cenários."
        )
    else:
        print(
            f"Foram encontrados {problemas} cenários "
            "com resultados diferentes."
        )


if __name__ == "__main__":
    main()