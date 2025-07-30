from typing import Callable

import pandas as pd
from ..ciga import TGraph
from .graph_community_analysis import graph_community_leiden
from tqdm import tqdm


def sequential_analysis(tg: TGraph,
                        cluster_func: Callable[..., pd.DataFrame],
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
    :param analysis_kwargs:
    :return:
    """
    results = pd.DataFrame()
    # add position columns to results
    for col in tg._position:
        results[col] = []
    results['character'] = []
    results['community'] = []

    # get time steps
    time_steps = tg.data.index.unique().tolist()
    if start:
        time_steps = [step for step in time_steps if step >= start]
    if end:
        time_steps = [step for step in time_steps if step <= end]

    for step in tqdm(time_steps, desc='Processing time steps', unit='step'):
        graph = tg.get_graph(step, normalized=w_normalized)

        communities = cluster_func(graph, **analysis_kwargs)
        for col, val in zip(tg._position, step):
            communities[col] = val

        results = pd.concat([results, communities], axis=0).reset_index(drop=True)

    return results

def tgraph_community_leiden(tgraph: TGraph, *,
                            accumulate=True,
                            start=None,
                            end=None,
                            weights='weight') -> pd.DataFrame:

    return sequential_analysis(tgraph, graph_community_leiden, accumulate=accumulate, start=start, end=end,
                               weights=weights)
