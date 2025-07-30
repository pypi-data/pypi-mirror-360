import warnings

import pandas as pd
import numpy as np
from igraph import Graph

class TGraph:

    def __init__(self, init_graph=None, data=None, position=None, directed=True):
        if data is None:
            raise ValueError("Data must be provided.")
        if position is None:
            raise ValueError("Position must be provided.")
        if 'weight' not in data.columns:
            raise ValueError("Weight column not found in data. Run calculate_weights() first.")

        self.data = data.copy()
        self._position = position
        self._layout = None
        self._directed = directed
        self._vnames = []
        self.name_to_id = {}
        self.id_to_name = {}
        self._cache_graph = None
        self._cache_time_point = tuple([-np.inf] * len(self._position))

        # set multi index if not already
        if not isinstance(self.data.index, pd.MultiIndex):
            self.data.set_index(list(self._position), inplace=True)

        if not self._directed:
            idx = self.data['source'] > self.data['target']
            self.data.loc[idx, ['source', 'target']] = self.data.loc[idx, ['target', 'source']].values

        if init_graph is None:
            self._init_graph = Graph(directed=self._directed)
            self._init_graph.vs['name'] = []
        else:
            self._init_graph = init_graph
            self._directed = init_graph.is_directed()

        # create name to id mapping
        self._vnames = self._init_graph.vs['name']
        self._create_vnames()

        self._cache_graph = self._init_graph.copy()

    def _create_vnames(self):
        self.name_to_id = {name: idx for idx, name in enumerate(self._vnames)}
        self.id_to_name = {idx: name for idx, name in enumerate(self._vnames)}

        return self._vnames

    @property
    def is_directed(self):
        return self._directed

    def _normalize_graph_weight(self, graph):
        total_weight = max(graph.es['weight'])
        if total_weight > 0:
            graph.es['weight'] = [w / total_weight for w in graph.es['weight']]
        else:
            warnings.warn("Total weight is 0. No normalization is done.")
        return graph

    def _invert_graph_weight(self, graph):
        weights = np.array(graph.es['weight'])
        adjusted_weights = 1 / (weights + 1e-6)
        graph.es['weight'] = adjusted_weights
        return graph

    def get_graph(self, time_point=None, *, accumulate=True, normalized=False, invert_weight=False, fade_function=None, fade_step=None):
        if time_point is None:
            time_point = tuple([np.inf] * len(self._position))
        if len(time_point) < len(self._position):
            time_point = tuple(list(time_point) + [np.inf] * (len(self._position) - len(time_point)))

        def adjust_graph_weight(graph):
            if normalized:
                graph = self._normalize_graph_weight(graph)
            if invert_weight:
                graph = self._invert_graph_weight(graph)
            return graph

        # def invert_graph_weight(graph):
        #     if invert_weight:
        #         new_graph = graph.copy()
        #         weights = np.array(new_graph.es['weight'])
        #         adjusted_weights = 1 / (weights + 1e-6)
        #         new_graph.es['weight'] = adjusted_weights
        #         return new_graph
        #     else:
        #         return graph

        # only provide changes of each time point
        if not accumulate:
            if fade_function is not None:
                raise ValueError("Fade function is not supported for non-accumulative graphs.")
            moment_graph = Graph(directed=self._directed)
            moment_graph.vs['name'] = []
            idx = pd.IndexSlice
            # get sub data where position contains time_point
            moment_data = self.data.loc[idx[time_point], :].copy()
            if moment_data.empty:
                return None
            self._update_graph(moment_graph, moment_data)
            return adjust_graph_weight(moment_graph)

        if fade_function is None:
            if self._cache_time_point and self._cache_time_point < time_point:
                start = list(self._cache_time_point)
                start[-1] += 1
                delta_data = self.take_interval(start=start, end=time_point)
            else:
                delta_data = self.take_interval(start=None, end=time_point)
                self._cache_graph = self._init_graph.copy()
                # also reset the name to id mapping

            if delta_data.empty:
                return adjust_graph_weight(self._cache_graph.copy())

            self._update_graph(self._cache_graph, delta_data)
            self._cache_time_point = time_point

            return adjust_graph_weight(self._cache_graph.copy())
        else:
            self._cache_graph = self._init_graph.copy()

            fading_data = self.take_interval(start=None, end=time_point)
            if fading_data.empty:
                return adjust_graph_weight(self._cache_graph.copy())

            # Reset index to access time positions as columns
            # fading_data = fading_data.reset_index()

            fading_graph = self._init_graph.copy()

            if isinstance(fade_step, list):
                start = [-np.inf] * len(self._position)
                idx = pd.IndexSlice
                for step in fade_step:
                    fading_data.loc[idx[tuple(start): tuple(step)], 'weight'] = \
                        fading_data.loc[idx[tuple(start): tuple(step)], ['weight']].apply(fade_function, axis=1)
                    # apply fade function to fading_graph.edges
                    if fading_graph.ecount() > 0:
                        fading_graph.es['weight'] = [fade_function(edge) for edge in fading_graph.es['weight']]
            elif isinstance(fade_step, tuple):
                # if fade_step not a sublist of self._position, raise error
                if not all([step in self._position for step in fade_step]):
                    raise ValueError("Fade step must be a sublist of position columns.")
                # group by fade_step, and apply fade function to group 1, grou 1+2, group 1+2+3, ...
                grouped = fading_data.groupby(list(fade_step))
                # apply fade function to 1 to n groups
                all_group_keys = list(grouped.groups.keys())
                for i, key in enumerate(all_group_keys):
                    # fade all groups before <=i
                    selected_group_keys = all_group_keys[:i+1]
                    mask = fading_data.index.isin(selected_group_keys, level=list(fade_step))
                    fading_data.loc[mask, 'weight'] = fading_data.loc[mask, 'weight'].apply(fade_function)
                    if fading_graph.ecount() > 0:
                        fading_graph.es['weight'] = [fade_function(edge) for edge in fading_graph.es['weight']]
            self._update_graph(fading_graph, fading_data)
            # return fading_graph
            return adjust_graph_weight(fading_graph)

    def graph_sub(self, graph1, graph2):
        # subtract weights of graph2 from graph1
        # when weight of edge is 0, remove the edge
        # when node has no edge, remove the node
        # Ensure both graphs are directed or undirected in the same way
        if graph1.is_directed() != graph2.is_directed():
            raise ValueError("Both graphs must be either directed or undirected.")

        # Copy graph1 to avoid modifying the original graph
        result_graph = graph1.copy()

        # Ensure that 'name' attribute exists in both graphs
        if 'name' not in result_graph.vs.attributes() or 'name' not in graph2.vs.attributes():
            raise ValueError("Both graphs must have 'name' attribute for vertices.")

        # Build a dictionary for quick edge weight lookup in graph2
        # Key: (source_name, target_name), Value: weight
        graph2_edge_weights = {}
        for e in graph2.es:
            source_name = graph2.vs[e.source]['name']
            target_name = graph2.vs[e.target]['name']
            key = (source_name, target_name)
            graph2_edge_weights[key] = e['weight']

        # Now, subtract weights in result_graph
        edges_to_delete = []
        for e in result_graph.es:
            source_name = result_graph.vs[e.source]['name']
            target_name = result_graph.vs[e.target]['name']
            key = (source_name, target_name)

            # Get the weight to subtract from graph2 if the edge exists
            weight_to_subtract = graph2_edge_weights.get(key, 0)

            # Subtract the weights
            new_weight = e['weight'] - weight_to_subtract

            if new_weight == 0:
                # Mark edge for deletion
                edges_to_delete.append(e.index)
            else:
                # Update the edge weight
                e['weight'] = new_weight

        # Delete edges with zero or negative weights
        result_graph.delete_edges(edges_to_delete)

        # Remove isolated vertices (nodes with no edges)
        degrees = result_graph.degree()
        isolated_vertices = [idx for idx, deg in enumerate(degrees) if deg == 0]
        result_graph.delete_vertices(isolated_vertices)

        return result_graph

    def get_delta_graph(self, start=None, end=None, *, delta_of_normalized=False, normalize_weight=False, invert_weight=False, fade_function=None, fade_step=None):
        # excluding the change at start time point
        # this should not change any data in the tgraph

        if delta_of_normalized or fade_function is not None:
            g1 = self.get_graph(time_point=start, normalized=delta_of_normalized, fade_function=fade_function, fade_step=fade_step)
            g2 = self.get_graph(time_point=end, normalized=delta_of_normalized, fade_function=fade_function, fade_step=fade_step)
            return self.graph_sub(g2, g1)
        else:
            if start is not None and len(start) == len(self._position):
                start = list(start)
                start[-1] += 1

            delta_data = self.take_interval(start=start, end=end)
            if delta_data.empty:
                interval_graph = Graph(directed=self._directed)
            else:
                agg_data = delta_data.groupby(['source', 'target'], as_index=False)['weight'].sum()
                nodes = set(agg_data['source']).union(set(agg_data['target']))
                temp_node_to_id = {node: idx for idx, node in enumerate(nodes)}

                agg_data['source_id'] = agg_data['source'].map(temp_node_to_id)
                agg_data['target_id'] = agg_data['target'].map(temp_node_to_id)

                edges = list(zip(agg_data['source_id'], agg_data['target_id']))
                weights = agg_data['weight'].tolist()

                interval_graph = Graph(edges=edges, directed=self._directed)
                interval_graph.vs['name'] = list(temp_node_to_id.keys())
                interval_graph.es['weight'] = weights

            if normalize_weight:
                interval_graph = self._normalize_graph_weight(interval_graph)
            if invert_weight:
                interval_graph = self._invert_graph_weight(interval_graph)
            return interval_graph

    def _update_graph(self, graph, data):
        agg_data = data.groupby(['source', 'target'], as_index=False)['weight'].sum()

        # NEW IMPLEMENTATION
        existing_nodes = set(graph.vs['name'])
        new_nodes = set(agg_data['source']).union(set(agg_data['target'])) - set(existing_nodes)

        # add new nodes to graph, also to self._vnames
        if new_nodes:
            graph.add_vertices(list(new_nodes))
            self._vnames = graph.vs['name']  # keep _vnames the newest
            # update name to id mapping, start from the last index
            for idx, node in enumerate(new_nodes, start=len(existing_nodes)):
                self.name_to_id[node] = idx
                self.id_to_name[idx] = node

        # add columns for source and target ids
        agg_data['source_id'] = agg_data['source'].map(self.name_to_id)
        agg_data['target_id'] = agg_data['target'].map(self.name_to_id)

        # use igraph to handle edge existence
        edges_in_data = list(zip(agg_data['source_id'], agg_data['target_id']))
        whether_edge_exists = graph.get_eids(pairs=edges_in_data, error=False)
        # get edge ids
        agg_data['eid'] = whether_edge_exists

        new_edges = agg_data[agg_data['eid'] == -1][['source_id', 'target_id']].values.tolist()
        new_weights = agg_data[agg_data['eid'] == -1]['weight'].tolist()

        existing_edge_ids_to_update = agg_data[agg_data['eid'] != -1]['eid'].tolist()
        weight_updates = agg_data[agg_data['eid'] != -1]['weight'].tolist()

        # existing_edges = graph.get_edgelist()
        # edges_in_data = pd.DataFrame(existing_edges, columns=['source_id', 'target_id'])
        #
        # # merge to identify existing and new edges
        # df_merged = pd.merge(
        #     agg_data,
        #     edges_in_data,
        #     on=['source_id', 'target_id'],
        #     how='left',
        #     indicator=True
        # )
        #
        # df_new_edges = df_merged[df_merged['_merge'] == 'left_only']
        # df_to_update = df_merged[df_merged['_merge'] == 'both']

        # new_edges = list(zip(df_new_edges['source_id'], df_new_edges['target_id']))
        # get those with eid value of -1 for new edges
        # new_weights = df_new_edges['weight'].tolist()
        # edges_to_update = list(zip(df_to_update['source_id'], df_to_update['target_id']))
        # edges to update are those with eid value not equal to -1
        # existing_edge_ids_to_update = graph.get_eids(pairs=edges_to_update, directed=graph.is_directed())
        # weight_updates = df_to_update['weight'].tolist()

        # Add new edges in bulk
        if new_edges:
            graph.add_edges(new_edges)
            # Set weights for new edges
            new_edge_ids = graph.es[-len(new_edges):].indices
            graph.es[new_edge_ids]['weight'] = new_weights

        # Update weights of existing edges in bulk
        if existing_edge_ids_to_update:
            # Retrieve current weights
            current_weights = graph.es[existing_edge_ids_to_update]['weight']
            # Update weights
            updated_weights = [cw + w for cw, w in zip(current_weights, weight_updates)]
            graph.es[existing_edge_ids_to_update]['weight'] = updated_weights

        return graph

    def take_interval(self, start=None, end=None):
        if start is None:
            start = [-np.inf] * len(self._position)
        else:
            if len(start) < len(self._position):
                start = list(start) + [None] * (len(self._position) - len(start))
            start = [s if s is not None else -np.inf for s in start]

        if end is None:
            end = [np.inf] * len(self._position)
        else:
            if len(end) < len(self._position):
                end = list(end) + [None] * (len(self._position) - len(end))
            end = [e if e is not None else np.inf for e in end]

        if len(self._position) > len(start) or len(self._position) > len(end):
            raise ValueError("The length of 'start/end' is out of range.")

        idx = pd.IndexSlice
        filtered_data = self.data.loc[idx[tuple(start): tuple(end)], :].copy()

        return filtered_data


