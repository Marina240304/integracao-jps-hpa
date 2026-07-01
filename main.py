from math import isclose

from src.astar import buscar_caminho
from src.grid import Grid, Posicao
from src.hpa_busca import buscar_hpa
from src.hpa_jps import buscar_hpa_jps
from src.jps import buscar_caminho_jps


def mostrar_mapa(
    grid: Grid,
    inicio: Posicao,
    destino: Posicao,
    caminho: list[Posicao],
    nome_algoritmo: str,
) -> None:
    """
    Exibe o mapa no terminal.

    I = início
    D = destino
    # = obstáculo
    * = caminho
    . = célula livre
    """

    posicoes_caminho = set(caminho)

    print(f"\nMapa — {nome_algoritmo}:")

    for linha in range(grid.quantidade_linhas):
        simbolos = []

        for coluna in range(grid.quantidade_colunas):
            posicao = (linha, coluna)

            if posicao == inicio:
                simbolos.append("I")
            elif posicao == destino:
                simbolos.append("D")
            elif posicao in posicoes_caminho:
                simbolos.append("*")
            elif grid.celulas[linha][coluna] == 1:
                simbolos.append("#")
            else:
                simbolos.append(".")

        print(" ".join(simbolos))


def mostrar_resultado_astar(resultado) -> None:
    print("\n===== RESULTADO DO A* =====")
    print(f"Caminho encontrado: {resultado.encontrado}")

    if resultado.encontrado:
        print(f"Custo: {resultado.custo:.3f}")
        print(
            f"Posições no caminho: "
            f"{len(resultado.caminho)}"
        )
        print(
            f"Nós expandidos: "
            f"{resultado.nos_expandidos}"
        )
        print(
            f"Tempo: "
            f"{resultado.tempo_segundos:.8f} segundos"
        )


def mostrar_resultado_jps(resultado) -> None:
    print("\n===== RESULTADO DO JPS =====")
    print(f"Caminho encontrado: {resultado.encontrado}")

    if resultado.encontrado:
        print(f"Custo: {resultado.custo:.3f}")
        print(
            f"Posições no caminho: "
            f"{len(resultado.caminho)}"
        )
        print(
            f"Nós expandidos: "
            f"{resultado.nos_expandidos}"
        )
        print(
            f"Jump Points identificados: "
            f"{resultado.jump_points_identificados}"
        )
        print(
            f"Tempo: "
            f"{resultado.tempo_segundos:.8f} segundos"
        )


def mostrar_resultado_hpa(resultado) -> None:
    print("\n===== RESULTADO DO HPA* =====")
    print(f"Caminho encontrado: {resultado.encontrado}")

    if resultado.encontrado:
        print(f"Custo: {resultado.custo:.3f}")
        print(
            f"Posições no caminho: "
            f"{len(resultado.caminho)}"
        )
        print(
            f"Nós expandidos totais: "
            f"{resultado.nos_expandidos}"
        )
        print(
            f"Nós expandidos no grafo abstrato: "
            f"{resultado.nos_expandidos_abstratos}"
        )
        print(
            f"Quantidade de portais: "
            f"{resultado.quantidade_portais}"
        )
        print(
            f"Nós do grafo abstrato: "
            f"{resultado.tamanho_grafo_abstrato}"
        )
        print(
            f"Arestas do grafo abstrato: "
            f"{resultado.quantidade_arestas_abstratas}"
        )
        print(
            f"Tempo: "
            f"{resultado.tempo_segundos:.8f} segundos"
        )


def mostrar_resultado_hpa_jps(resultado) -> None:
    print("\n===== RESULTADO DO HPA-JPS =====")
    print(f"Caminho encontrado: {resultado.encontrado}")

    if resultado.encontrado:
        print(f"Custo: {resultado.custo:.3f}")
        print(
            f"Posições no caminho: "
            f"{len(resultado.caminho)}"
        )
        print(
            f"Nós expandidos totais: "
            f"{resultado.nos_expandidos}"
        )
        print(
            f"Nós expandidos no grafo abstrato: "
            f"{resultado.nos_expandidos_abstratos}"
        )
        print(
            f"Quantidade de portais: "
            f"{resultado.quantidade_portais}"
        )
        print(
            f"Nós do grafo abstrato: "
            f"{resultado.tamanho_grafo_abstrato}"
        )
        print(
            f"Arestas do grafo abstrato: "
            f"{resultado.quantidade_arestas_abstratas}"
        )
        print(
            f"Jump Points identificados: "
            f"{resultado.jump_points_identificados}"
        )
        print(
            f"Tempo: "
            f"{resultado.tempo_segundos:.8f} segundos"
        )


def mostrar_comparacao(
    resultado_astar,
    resultado_jps,
    resultado_hpa,
    resultado_hpa_jps,
) -> None:
    print("\n===== COMPARAÇÃO DOS ALGORITMOS =====")

    print(
        f"{'Algoritmo':<12}"
        f"{'Custo':<12}"
        f"{'Caminho':<12}"
        f"{'Expandidos':<14}"
        f"{'Tempo (s)':<15}"
    )

    print("-" * 65)

    resultados = [
        ("A*", resultado_astar),
        ("JPS", resultado_jps),
        ("HPA*", resultado_hpa),
        ("HPA-JPS", resultado_hpa_jps),
    ]

    for nome, resultado in resultados:
        if resultado.encontrado:
            print(
                f"{nome:<12}"
                f"{resultado.custo:<12.3f}"
                f"{len(resultado.caminho):<12}"
                f"{resultado.nos_expandidos:<14}"
                f"{resultado.tempo_segundos:<15.8f}"
            )
        else:
            print(
                f"{nome:<12}"
                f"{'Não achou':<12}"
                f"{'-':<12}"
                f"{resultado.nos_expandidos:<14}"
                f"{resultado.tempo_segundos:<15.8f}"
            )

    resultados_encontrados = [
        resultado
        for _, resultado in resultados
        if resultado.encontrado
    ]

    if len(resultados_encontrados) != 4:
        print(
            "\nNem todos os algoritmos encontraram "
            "um caminho."
        )
        return

    custo_referencia = resultado_astar.custo

    custos_iguais = all(
        isclose(
            resultado.custo,
            custo_referencia,
            rel_tol=1e-9,
            abs_tol=1e-9,
        )
        for resultado in resultados_encontrados
    )

    if custos_iguais:
        print(
            "\nOs quatro algoritmos encontraram "
            "caminhos com o mesmo custo."
        )
    else:
        print(
            "\nOs algoritmos encontraram caminhos "
            "com custos diferentes."
        )


def main() -> None:
    matriz = [
        [0, 0, 0, 0, 0],
        [0, 1, 0, 1, 0],
        [0, 1, 0, 0, 0],
        [0, 0, 0, 1, 0],
        [0, 0, 0, 0, 0],
    ]

    grid = Grid.criar(matriz)

    inicio = (4, 0)
    destino = (0, 4)

    tamanho_cluster = 3

    print("===== CONFIGURAÇÃO DO TESTE =====")
    print(
        f"Tamanho do mapa: "
        f"{grid.quantidade_linhas} x "
        f"{grid.quantidade_colunas}"
    )
    print(f"Início: {inicio}")
    print(f"Destino: {destino}")
    print(
        f"Tamanho dos clusters: "
        f"{tamanho_cluster} x {tamanho_cluster}"
    )

    resultado_astar = buscar_caminho(
        grid=grid,
        inicio=inicio,
        destino=destino,
    )

    resultado_jps = buscar_caminho_jps(
        grid=grid,
        inicio=inicio,
        destino=destino,
    )

    resultado_hpa = buscar_hpa(
        grid=grid,
        inicio=inicio,
        destino=destino,
        tamanho_cluster=tamanho_cluster,
    )

    resultado_hpa_jps = buscar_hpa_jps(
        grid=grid,
        inicio=inicio,
        destino=destino,
        tamanho_cluster=tamanho_cluster,
    )

    mostrar_resultado_astar(resultado_astar)
    mostrar_resultado_jps(resultado_jps)
    mostrar_resultado_hpa(resultado_hpa)
    mostrar_resultado_hpa_jps(resultado_hpa_jps)

    if resultado_astar.encontrado:
        mostrar_mapa(
            grid=grid,
            inicio=inicio,
            destino=destino,
            caminho=resultado_astar.caminho,
            nome_algoritmo="A*",
        )

    if resultado_jps.encontrado:
        mostrar_mapa(
            grid=grid,
            inicio=inicio,
            destino=destino,
            caminho=resultado_jps.caminho,
            nome_algoritmo="JPS",
        )

    if resultado_hpa.encontrado:
        mostrar_mapa(
            grid=grid,
            inicio=inicio,
            destino=destino,
            caminho=resultado_hpa.caminho,
            nome_algoritmo="HPA*",
        )

    if resultado_hpa_jps.encontrado:
        mostrar_mapa(
            grid=grid,
            inicio=inicio,
            destino=destino,
            caminho=resultado_hpa_jps.caminho,
            nome_algoritmo="HPA-JPS",
        )

    mostrar_comparacao(
        resultado_astar=resultado_astar,
        resultado_jps=resultado_jps,
        resultado_hpa=resultado_hpa,
        resultado_hpa_jps=resultado_hpa_jps,
    )


if __name__ == "__main__":
    main()