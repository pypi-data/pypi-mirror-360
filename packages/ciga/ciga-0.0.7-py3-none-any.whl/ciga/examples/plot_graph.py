import ciga as cg
import pandas as pd
import matplotlib.pyplot as plt
from viztracer import VizTracer

df = pd.read_csv('../../m_data.csv')

# custom weight function
# input: interaction (str)
# output: weight (float)
def weight_func(interaction):
    return 1

tracer = VizTracer()
tracer.start()

# load data without weight
interactions = cg.prepare_data(df, ('Season', 'Episode', 'Scene', 'Line'),
                                source='Speaker', target='Listener', interaction='Words')
sub_interactions = cg.segment(interactions, start=(1, 1, 1, 1), end=(2, 1, 1, 1))

# calculate weight
weights = cg.calculate_weights(sub_interactions, weight_func=weight_func)

# adjust grain size
agg_weights = cg.agg_weights(weights, ('Season', 'Episode', 'Scene', 'Line'), agg_func=lambda x: sum(x))

# create network
tg = cg.TGraph(data=agg_weights, position=('Season', 'Episode', 'Scene', 'Line'), directed=True)

# print(tg.data)
# graph = tg.get_graph((1, 1, 2))'
graph = tg.get_graph((2, 1, 1, 1), invert_weight=False, normalized=False)
# graph = tg.get_graph(fade_function=lambda x: x*0.5, fade_step=[(1, 2, 2, 2)])
# graph = tg.get_delta_graph((1, 1, 1, 1), (2, 1, 1, 1), fade_function=lambda x: x, fade_step=[(1, 2, 2, 2)])
# graph = tg.get_delta_graph((1, 1, 1, 1), (2, 1, 1, 1))

# fig, ax = plt.subplots()
# cg.iplot(graph, target=ax)

tracer.stop()
tracer.save()

# plt.show()

cg.pyviz(graph, notebook=False, output_file='graph.html')