import igraph as ig
import pandas as pd
import numpy as np


# Full graph analysis
def graph_degree(graph: ig.Graph, weighted=False, normalized=False) -> pd.DataFrame:
    """
    Calculate various degree centrality measures for each vertex in the graph.

    This function computes degree-based centrality metrics, including in-degree, out-degree,
    total degree, and their weighted counterparts for directed graphs. For undirected graphs,
    it calculates the degree and weighted degree centrality. Additionally, it supports
    normalization of these centrality measures based on the number of vertices in the graph.

    Parameters:
        graph (igraph.Graph):
            The input graph on which degree centrality measures are to be computed.
            Must be an instance of igraph's `Graph` class.

        weighted (bool, optional):
            If set to `True`, the function calculates weighted degree centrality
            using edge weights. Defaults to `False`.

        normalized (bool, optional):
            If set to `True`, the degree centrality measures are normalized by
            dividing by (n-1), where n is the number of vertices in the graph.
            This normalization facilitates comparison across graphs of different sizes.
            Defaults to `False`.

    Returns:
        pd.DataFrame:
            A pandas DataFrame containing the calculated degree centrality measures.
            The columns vary based on whether the graph is directed and whether
            weighting and normalization are applied.

            - For **directed graphs**:
                - `in_degree`: Number of incoming edges per vertex.
                - `out_degree`: Number of outgoing edges per vertex.
                - `all_degree`: Total degree (in-degree + out-degree) per vertex.
                - `weighted_in_degree` *(if `weighted=True`)*: Sum of weights of incoming edges.
                - `weighted_out_degree` *(if `weighted=True`)*: Sum of weights of outgoing edges.
                - `weighted_all_degree` *(if `weighted=True`)*: Sum of weights of all edges.

            - For **undirected graphs**:
                - `degree`: Number of edges per vertex.
                - `weighted_degree` *(if `weighted=True`)*: Sum of weights of edges per vertex.

            - **Normalization** *(if `normalized=True`)*:
                - Additional columns prefixed with `normalized_` representing the normalized
                  centrality measures (e.g., `normalized_degree`, `normalized_in_degree`, etc.).

    Raises:
        ValueError:
            - If the graph does not contain edge weights but `weighted=True` is specified.

    Example:
        ```python
        import igraph as ig
        import pandas as pd
        from ciga.analysis.graph_centrality_analysis import graph_degree

        # Create a sample directed graph
        g = ig.Graph(directed=True)
        g.add_vertices(4)
        g.vs['name'] = ['A', 'B', 'C', 'D']
        g.add_edges([('A', 'B'), ('B', 'C'), ('C', 'A'), ('A', 'D')])
        g.es['weight'] = [1.5, 2.0, 2.5, 1.0]

        # Calculate degree centrality
        degree_df = graph_degree(g, weighted=True, normalized=True)
        print(degree_df)
        ```
    """
    result = pd.DataFrame()
    directed = graph.is_directed()
    normalize_factor = graph.vcount() - 1
    if directed:
        in_degree = graph.degree(mode='in')
        out_degree = graph.degree(mode='out')
        all_degree = graph.degree(mode='all')
        result['in_degree'] = in_degree
        result['out_degree'] = out_degree
        result['all_degree'] = all_degree

        if weighted:
            weighted_in_degree = graph.strength(mode='in', weights='weight')
            weighted_out_degree = graph.strength(mode='out', weights='weight')
            weighted_all_degree = graph.strength(mode='all', weights='weight')
            result['weighted_in_degree'] = weighted_in_degree
            result['weighted_out_degree'] = weighted_out_degree
            result['weighted_all_degree'] = weighted_all_degree
    else:
        graph_degree = graph.degree()
        result['degree'] = graph_degree

        if weighted:
            weighted_degree = graph.strength(weights='weight')
            result['weighted_degree'] = weighted_degree

    if normalized:
        if directed:
            result['normalized_in_degree'] = result['in_degree'] / normalize_factor
            result['normalized_out_degree'] = result['out_degree'] / normalize_factor
            result['normalized_all_degree'] = result['all_degree'] / normalize_factor
            if weighted:
                result['normalized_weighted_in_degree'] = result['weighted_in_degree'] / normalize_factor
                result['normalized_weighted_out_degree'] = result['weighted_out_degree'] / normalize_factor
                result['normalized_weighted_all_degree'] = result['weighted_all_degree'] / normalize_factor
        else:
            result['normalized_degree'] = result['degree'] / normalize_factor
            if weighted:
                result['normalized_weighted_degree'] = result['weighted_degree'] / normalize_factor

    # print(result)
    return result


def graph_betweenness(graph: ig.Graph, weighted=False, cutoff=None, sources=None, targets=None,
                      normalized=False) -> pd.DataFrame:
    """
    Compute betweenness centrality for each vertex in the graph.

    This function calculates the betweenness centrality, which measures the extent to
    which a vertex lies on paths between other vertices. It supports both weighted and
    unweighted graphs and allows for normalization of the centrality scores. Additional
    parameters enable customization of the computation, such as limiting the analysis to
    specific sources, targets, or path lengths.

    Parameters:
        graph (igraph.Graph):
            The input graph on which betweenness centrality is to be computed.
            Must be an instance of igraph's `Graph` class.

        weighted (bool, optional):
            If set to `True`, the function calculates weighted betweenness centrality
            using edge weights. Defaults to `False`.

        cutoff (int, optional):
            Specifies the maximum path length to consider when calculating betweenness.
            Paths longer than the cutoff are ignored. Defaults to `None`, which considers
            all possible paths.

        sources (list, optional):
            A list of vertex indices to be used as sources for the betweenness calculation.
            If specified, only paths originating from these sources are considered. Defaults to `None`,
            which includes all vertices as potential sources.

        targets (list, optional):
            A list of vertex indices to be used as targets for the betweenness calculation.
            If specified, only paths ending at these targets are considered. Defaults to `None`,
            which includes all vertices as potential targets.

        normalized (bool, optional):
            If set to `True`, the betweenness centrality scores are normalized by dividing by
            the number of possible pairs of vertices not including the vertex itself. This makes
            the centrality scores comparable across graphs of different sizes. Defaults to `False`.

    Returns:
        pd.DataFrame:
            A pandas DataFrame containing the calculated betweenness centrality measures.
            The DataFrame includes the following columns based on the input parameters:

            - `betweenness`: Unweighted betweenness centrality.
            - `weighted_betweenness` *(if `weighted=True`)*: Weighted betweenness centrality.

            If `normalized=True`, additional columns with normalized scores are included:
            - `normalized_betweenness`
            - `normalized_weighted_betweenness` *(if `weighted=True`)*

    Raises:
        ValueError:
            - If the graph does not contain edge weights but `weighted=True` is specified.
            - If `sources` or `targets` contain invalid vertex indices.

    Example:
        ```python
        import igraph as ig
        import pandas as pd
        from ciga.analysis.graph_centrality_analysis import graph_betweenness

        # Create a sample undirected graph
        g = ig.Graph(edges=[(0, 1), (1, 2), (2, 3), (3, 0), (1, 3)])
        g.vs['name'] = ['A', 'B', 'C', 'D']
        g.es['weight'] = [1, 2, 1, 3, 2]

        # Calculate betweenness centrality
        betweenness_df = graph_betweenness(g, weighted=True, normalized=True)
        print(betweenness_df)
        ```
    """
    result = pd.DataFrame()
    directed = graph.is_directed()
    betweenness = graph.betweenness(weights=None, directed=directed, cutoff=cutoff, sources=sources, targets=targets)
    result['betweenness'] = betweenness
    if weighted:
        weighted_betweenness = graph.betweenness(weights='weight', directed=directed, cutoff=cutoff, sources=sources,
                                                 targets=targets)
        result['weighted_betweenness'] = weighted_betweenness

    if normalized:
        # Normalization factors based on whether the graph is directed
        n = graph.vcount()
        if directed:
            normalize_factor = (n - 1) * (n - 2)
        else:
            normalize_factor = (n - 1) * (n - 2) / 2

        result['normalized_betweenness'] = result['betweenness'] / normalize_factor
        if weighted:
            result['normalized_weighted_betweenness'] = result['weighted_betweenness'] / normalize_factor

    return result


def graph_closeness(graph: ig.Graph, weighted, cutoff=None, normalized=False) -> pd.DataFrame:
    """
    Calculate closeness centrality measures for each vertex in the graph.

    Closeness centrality assesses how close a vertex is to all other vertices in the graph.
    It is defined as the reciprocal of the sum of the shortest path distances from the vertex
    to all other vertices. This function supports both weighted and unweighted graphs and
    allows for normalization of the closeness scores. Additionally, it offers the ability to
    limit the analysis to paths within a specified cutoff and to compute centrality for specific
    modes (in, out, all) in directed graphs.

    Parameters:
        graph (igraph.Graph):
            The input graph on which closeness centrality is to be computed.
            Must be an instance of igraph's `Graph` class.

        weighted (bool):
            If set to `True`, the function calculates weighted closeness centrality
            using edge weights. Must be explicitly provided (no default value).

        cutoff (int, optional):
            Specifies the maximum path length to consider when calculating closeness.
            Paths longer than the cutoff are ignored. Defaults to `None`, which considers
            all possible paths.

        normalized (bool, optional):
            If set to `True`, the closeness centrality scores are normalized based on
            the number of reachable vertices. This makes the centrality scores comparable
            across graphs of different sizes and densities. Defaults to `False`.

    Returns:
        pd.DataFrame:
            A pandas DataFrame containing the calculated closeness centrality measures.
            The columns vary based on whether the graph is directed and whether
            weighting and normalization are applied.

            - For **directed graphs**:
                - `in_closeness`: Closeness centrality based on incoming paths.
                - `out_closeness`: Closeness centrality based on outgoing paths.
                - `all_closeness`: Closeness centrality considering all paths.

                - `weighted_in_closeness` *(if `weighted=True`)*: Weighted in-closeness centrality.
                - `weighted_out_closeness` *(if `weighted=True`)*: Weighted out-closeness centrality.
                - `weighted_all_closeness` *(if `weighted=True`)*: Weighted all-closeness centrality.

            - For **undirected graphs**:
                - `closeness`: Closeness centrality.
                - `weighted_closeness` *(if `weighted=True`)*: Weighted closeness centrality.

            - **Normalization** *(if `normalized=True`)*:
                - Additional columns prefixed with `normalized_` representing the normalized
                  closeness centrality measures (e.g., `normalized_closeness`, `normalized_in_closeness`, etc.).

    Raises:
        ValueError:
            - If the graph does not contain edge weights but `weighted=True` is specified.

    Example:
        ```python
        import igraph as ig
        import pandas as pd
        from ciga.analysis.graph_centrality_analysis import graph_closeness

        # Create a sample directed graph
        g = ig.Graph(directed=True)
        g.add_vertices(3)
        g.vs['name'] = ['A', 'B', 'C']
        g.add_edges([('A', 'B'), ('B', 'C')])
        g.es['weight'] = [1, 2]

        # Calculate closeness centrality
        closeness_df = graph_closeness(g, weighted=True, normalized=True)
        print(closeness_df)
        ```
    """
    result = pd.DataFrame()
    directed = graph.is_directed()

    if directed:
        in_closeness = graph.closeness(weights=None, mode="in", cutoff=cutoff)
        out_closeness = graph.closeness(weights=None, mode="out", cutoff=cutoff)
        all_closeness = graph.closeness(weights=None, mode="all", cutoff=cutoff)
        result['in_closeness'] = in_closeness
        result['out_closeness'] = out_closeness
        result['all_closeness'] = all_closeness

        if weighted:
            weighted_in_closeness = graph.closeness(weights='weight', mode="in", cutoff=cutoff)
            weighted_out_closeness = graph.closeness(weights='weight', mode="out", cutoff=cutoff)
            weighted_all_closeness = graph.closeness(weights='weight', mode="all", cutoff=cutoff)
            result['weighted_in_closeness'] = weighted_in_closeness
            result['weighted_out_closeness'] = weighted_out_closeness
            result['weighted_all_closeness'] = weighted_all_closeness
    else:
        closeness = graph.closeness(weights=None, cutoff=cutoff)
        result['closeness'] = closeness

        if weighted:
            weighted_closeness = graph.closeness(weights='weight', cutoff=cutoff)
            result['weighted_closeness'] = weighted_closeness

    if normalized:
        if directed:
            normalized_in_closeness = graph.closeness(weights=None, mode="in", cutoff=cutoff, normalized=True)
            normalized_out_closeness = graph.closeness(weights=None, mode="out", cutoff=cutoff, normalized=True)
            normalized_all_closeness = graph.closeness(weights=None, mode="all", cutoff=cutoff, normalized=True)
            result['normalized_in_closeness'] = normalized_in_closeness
            result['normalized_out_closeness'] = normalized_out_closeness
            result['normalized_all_closeness'] = normalized_all_closeness

            if weighted:
                normalized_weighted_in_closeness = graph.closeness(weights='weight', mode="in", cutoff=cutoff,
                                                                   normalized=True)
                normalized_weighted_out_closeness = graph.closeness(weights='weight', mode="out", cutoff=cutoff,
                                                                    normalized=True)
                normalized_weighted_all_closeness = graph.closeness(weights='weight', mode="all", cutoff=cutoff,
                                                                    normalized=True)
                result['normalized_weighted_in_closeness'] = normalized_weighted_in_closeness
                result['normalized_weighted_out_closeness'] = normalized_weighted_out_closeness
                result['normalized_weighted_all_closeness'] = normalized_weighted_all_closeness
        else:
            normalized_closeness = graph.closeness(weights=None, cutoff=cutoff, normalized=True)
            result['normalized_closeness'] = normalized_closeness

            if weighted:
                normalized_weighted_closeness = graph.closeness(weights='weight', cutoff=cutoff, normalized=True)
                result['normalized_weighted_closeness'] = normalized_weighted_closeness

    return result


def graph_eigenvector_centrality(graph: ig.Graph, weighted=False, scale=True,
                                 return_eigenvalue=False) -> pd.DataFrame:
    """
    Compute eigenvector centrality for each vertex in the graph.

    Eigenvector centrality measures a vertex's influence based on the influence of its neighbors.
    It assigns relative scores to all vertices in the network based on the concept that connections
    to high-scoring vertices contribute more to the score of the vertex in question than connections
    to low-scoring vertices. This function supports both weighted and unweighted graphs, allows
    scaling of the centrality scores, and can optionally return the corresponding eigenvalues.

    Parameters:
        graph (igraph.Graph):
            The input graph on which eigenvector centrality is to be computed.
            Must be an instance of igraph's `Graph` class.

        weighted (bool, optional):
            If set to `True`, the function calculates eigenvector centrality
            using edge weights. Defaults to `False`.

        scale (bool, optional):
            If set to `True`, the centrality scores are scaled to have a mean of 0 and a
            variance of 1. Scaling can be useful for comparative analysis. Defaults to `True`.

        return_eigenvalue (bool, optional):
            If set to `True`, the function returns the principal eigenvalue associated
            with the eigenvector centrality calculation. This can provide insights into
            the graph's connectivity and structure. Defaults to `False`.

    Returns:
        pd.DataFrame:
            A pandas DataFrame containing the calculated eigenvector centrality measures.
            The columns included in the DataFrame depend on the input parameters.

            - `eigenvector_centrality`: The eigenvector centrality score for each vertex.
            - `eigenvalue` *(if `return_eigenvalue=True`)*: The principal eigenvalue associated with
              the eigenvector centrality computation.

    Raises:
        ValueError:
            - If the graph does not contain edge weights but `weighted=True` is specified.
            - If the graph is not strongly connected, making eigenvector centrality undefined.

    Example:
        ```python
        import igraph as ig
        import pandas as pd
        from ciga.analysis.graph_centrality_analysis import graph_eigenvector_centrality

        # Create a sample undirected graph
        g = ig.Graph(edges=[(0, 1), (1, 2), (2, 3), (3, 0), (1, 3)])
        g.vs['name'] = ['A', 'B', 'C', 'D']
        g.es['weight'] = [1, 2, 1, 3, 2]

        # Calculate eigenvector centrality
        eigen_df = graph_eigenvector_centrality(g, weighted=True, scale=True, return_eigenvalue=True)
        print(eigen_df)
        ```
    """
    result = pd.DataFrame()
    directed = graph.is_directed()

    weights = 'weight' if weighted else None
    centralities = graph.eigenvector_centrality(directed=directed, scale=scale, weights=weights,
                                                return_eigenvalue=return_eigenvalue)
    if return_eigenvalue:
        result['eigenvector_centrality'] = [c[0] for c in centralities]
        result['eigenvalue'] = [c[1] for c in centralities]
    else:
        result['eigenvector_centrality'] = centralities

    return result
