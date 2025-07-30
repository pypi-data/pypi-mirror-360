import pandas as pd


def graph_community_leiden(graph, weights='weight') -> pd.DataFrame:
    communities = graph.community_leiden(weights='weight')
    data = []
    for community_index, community in enumerate(communities):
        community_nodes = [graph.vs[node_id]['name'] for node_id in community]
        for node_name in community_nodes:
            data.append({
                    'character': node_name,
                    'community': community_index
                })
    result = pd.DataFrame(data)
    return result


# community = graph.community_multilevel(weights='weight')
# community = graph.community_leiden(weights='weight')
# community = graph.community_label_propagation(weights='weight')
