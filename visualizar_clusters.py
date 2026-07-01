from src.grid import Grid
from src.hpa import dividir_em_clusters, encontrar_cluster


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

    tamanho_cluster = 3

    clusters = dividir_em_clusters(
        grid=grid,
        tamanho_cluster=tamanho_cluster,
    )

    letras = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    print(
        f"Mapa: {grid.quantidade_linhas} x "
        f"{grid.quantidade_colunas}"
    )

    print(f"Tamanho dos clusters: {tamanho_cluster} x {tamanho_cluster}")
    print(f"Quantidade de clusters: {len(clusters)}")

    print("\nDivisão do mapa em clusters:\n")

    for linha in range(grid.quantidade_linhas):
        simbolos = []

        for coluna in range(grid.quantidade_colunas):
            posicao = (linha, coluna)

            cluster = encontrar_cluster(
                clusters,
                posicao,
            )

            if grid.celulas[linha][coluna] == 1:
                simbolos.append("#")
            elif cluster is not None:
                simbolos.append(
                    letras[cluster.identificador]
                )

        print(" ".join(simbolos))

    print("\nInformações dos clusters:")

    for cluster in clusters:
        letra = letras[cluster.identificador]

        print(
            f"Cluster {letra}: "
            f"linhas {cluster.linha_inicio} até "
            f"{cluster.linha_fim - 1}, "
            f"colunas {cluster.coluna_inicio} até "
            f"{cluster.coluna_fim - 1}"
        )


if __name__ == "__main__":
    main()