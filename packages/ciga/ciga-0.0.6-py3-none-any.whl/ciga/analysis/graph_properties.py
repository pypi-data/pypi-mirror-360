import pandas as pd


def graph_density(graph, loops=False) -> float:
    return graph.density(loops=loops)


# also called the clustering coefficient
def graph_transitivity_undirected(graph, mode='nan') -> float:
    if graph.is_directed():
        graph = graph.to_undirected(mode="collapse")
    return graph.transitivity_undirected(mode=mode)