from src.grid import Grid
from src.hpa import (
    dividir_em_clusters,
    identificar_portais,
)


def main() -> None:
    matriz = [
        [0, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 1, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0],
        [0, 1, 0, 0, 1, 0],
        [0, 0, 0, 0, 0, 0],
    ]

    grid = Grid.criar(matriz)

    clusters = dividir_em_clusters(
        grid=grid,
        tamanho_cluster=3,
    )

    portais = identificar_portais(
        grid=grid,
        clusters=clusters,
    )

    posicoes_portais = set()

    for portal in portais:
        posicoes_portais.add(
            portal.posicao_origem
        )

        posicoes_portais.add(
            portal.posicao_destino
        )

    print(f"Quantidade de portais: {len(portais)}")
    print("\nMapa com portais:\n")

    for linha in range(grid.quantidade_linhas):
        simbolos = []

        for coluna in range(
            grid.quantidade_colunas
        ):
            posicao = (linha, coluna)

            if posicao in posicoes_portais:
                simbolos.append("P")

            elif grid.celulas[linha][coluna] == 1:
                simbolos.append("#")

            else:
                simbolos.append(".")

        print(" ".join(simbolos))

    print("\nPortais identificados:")

    for indice, portal in enumerate(
        portais,
        start=1,
    ):
        print(
            f"Portal {indice}: "
            f"cluster {portal.cluster_origem} "
            f"{portal.posicao_origem} "
            f"<-> "
            f"cluster {portal.cluster_destino} "
            f"{portal.posicao_destino}"
        )

    print("\nLegenda:")
    print("P = célula pertencente a um portal")
    print("# = obstáculo")
    print(". = posição livre")


if __name__ == "__main__":
    main()