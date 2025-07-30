import pandas as pd
from typing import Callable, Dict, Any, List
from ..ciga import TGraph
from .graph_centrality_analysis import graph_degree, graph_betweenness, graph_closeness, graph_eigenvector_centrality
from tqdm import tqdm


def sequential_analysis(tg: TGraph,
                        analysis_func: Callable[..., pd.DataFrame],
                        *,
                        accumulate=True,
                        start=None,
                        end=None,
                        w_normalized=False,
                        **analysis_kwargs) -> pd.DataFrame:
    """
    Perform analysis on a time-varying graph sequentially.
    :param tg:
    :param analysis_func:
    :param accumulate: whether analysis results should be accumulated
    :param start:
    :param end:
    :param w_normalized: true if the indices should be obtained from a normalized graph
    :param analysis_kwargs:
    :return:
    """
    results = pd.DataFrame()
    # add position columns to results
    for col in tg._position:
        results[col] = []
    results['character'] = []

    # get time steps
    time_steps = tg.data.index.unique().tolist()
    if start:
        time_steps = [step for step in time_steps if step >= start]
    if end:
        time_steps = [step for step in time_steps if step <= end]

    for step in tqdm(time_steps, desc='Processing time steps', unit='step'):
        graph = tg.get_graph(step, accumulate=accumulate, normalized=w_normalized)

        measures = analysis_func(graph, **analysis_kwargs)
        for col, val in zip(tg._position, step):
            measures[col] = val
        measures['character'] = graph.vs['name']

        results = pd.concat([results, measures], axis=0).reset_index(drop=True)

    return results


def tgraph_degree(tgraph: TGraph, *,
                  start=None,
                  end=None,
                  accumulate=True,
                  weighted=False,
                  w_normalized=False,
                  normalized=False) -> pd.DataFrame:
    """
    Perform degree analysis on a time-varying graph.
    :param tgraph: time-varying graph
    :param start: start time step
    :param end: end time step
    :param accumulate: whether analysis results should be accumulated
    :param weighted: true if weighted degree is needed
    :param w_normalized: true if the indices should be obtained from a normalized graph
    :param normalized: true if normalized degree is needed
    """
    return sequential_analysis(tgraph, accumulate=accumulate, analysis_func=graph_degree, start=start, end=end,
                               weighted=weighted, w_normalized=w_normalized, normalized=normalized)


def tgraph_betweenness(tgraph: TGraph, *,
                       start=None,
                       end=None,
                       accumulate=True,
                       weighted=False,
                       w_normalized=False,
                       normalized=True,
                       cutoff=None,
                       sources=None,
                       targets=None) -> pd.DataFrame:
    return sequential_analysis(tgraph, accumulate=accumulate, analysis_func=graph_betweenness, start=start, end=end,
                               weighted=weighted, w_normalized=w_normalized, normalized=normalized, cutoff=cutoff,
                               sources=sources, targets=targets)


def tgraph_closeness(tgraph: TGraph, *,
                     start=None,
                     end=None,
                     accumulate=True,
                     weighted=False,
                     w_normalized=False,
                     normalized=True,
                     cutoff=None) -> pd.DataFrame:
    return sequential_analysis(tgraph, accumulate=accumulate, analysis_func=graph_closeness, start=start, end=end,
                               weighted=weighted, w_normalized=w_normalized, normalized=normalized, cutoff=cutoff)

def tgraph_eigenvector_centrality(tgraph: TGraph, *,
                                  start=None,
                                  end=None,
                                  accumulate=True,
                                  weighted=False,
                                  scale=True,
                                  return_eigenvalue=False,
                                  options=None) -> pd.DataFrame:
    return sequential_analysis(tgraph, accumulate=accumulate, analysis_func=graph_eigenvector_centrality,
                               start=start, end=end, weighted=weighted, scale=scale, return_eigenvalue=return_eigenvalue)
