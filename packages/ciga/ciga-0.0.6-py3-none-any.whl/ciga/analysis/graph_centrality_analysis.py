import igraph as ig
import pandas as pd
import numpy as np


# Full graph analysis
def graph_degree(graph: ig.Graph, weighted=False, normalized=False) -> pd.DataFrame:
    """
    Normalized degree is divided by n-1, where n is the number of vertices in the graph.
    As networkx
    :param graph:
    :param weighted:
    :param normalized: true if normalized degree is needed
    :return:
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
