import yaml
from pyvis.network import Network
import networkx as nx


def is_def(node_id):   return 'D' in node_id
def is_axiom(node_id): return 'A' in node_id
def is_prop(node_id):  return 'P' in node_id
def is_cor(node_id):   return 'c' in node_id
def is_schol(node_id): return 's' in node_id

def calc_node_levels(graph):

	def get_bottom_most_parent_level(node_id):
		parent_ids = graph[node_id]
		parent_ids = [pid for pid in parent_ids if not is_schol(pid)]  # ignore scholia
		bottom_most_parent_level = 2
		for pid in parent_ids:
			print(pid)
			if node_levels[pid] > bottom_most_parent_level:
				bottom_most_parent_level = node_levels[pid]
		return bottom_most_parent_level

	node_levels = {}
	for node_id in graph.keys():
		if is_def(node_id):
			level = 1
		elif is_axiom(node_id): 
			level = 2
		elif is_prop(node_id):
			bottom_most_parent_level = get_bottom_most_parent_level(node_id)
			level = bottom_most_parent_level + 1
		node_levels[node_id] = level

	return node_levels

def get_node_viz_attrs(graph):
	node_colors = {}
	node_shapes = {}
	for node_id in graph.keys():
		if is_def(node_id):
			color = '#EC7063'
		elif is_axiom(node_id):
			color = '#52BE80'
		elif is_prop(node_id):
			if is_cor(node_id): 
				color = '#AED6F1'
			else:
				color = '#2E86C1'
		node_colors[node_id] = color
		node_shapes[node_id] = 'circle'
	return node_colors, node_shapes


def run():

	with open("./logical.yaml") as fs:
		graph = yaml.safe_load(fs)
	with open("./text-en-curley.yaml") as fs:
		text = yaml.safe_load(fs)	

	node_levels = calc_node_levels(graph)
	node_colors, node_shapes = get_node_viz_attrs(graph)
	nx_graph = nx.DiGraph()

	for node_id in graph.keys():		
		if is_cor(node_id) or is_schol(node_id): description = ""
		else:                                    description = text[node_id]
		nx_graph.add_node(node_id, label=node_id, title=description, level=node_levels[node_id], 
			              shape=node_shapes[node_id], color=node_colors[node_id])
		parent_ids = graph[node_id]
		if parent_ids is None:   continue
		if len(parent_ids) == 0: continue		
		parent_ids = [pid for pid in parent_ids if not is_schol(pid)] # Ignore references to scholia  ##
		for parent_id in parent_ids:
			nx_graph.add_edge(parent_id, node_id)

	net = Network(directed=True, layout=True)
	net.from_nx(nx_graph)
	net.toggle_physics(True)
	net.show('ethica_map.html', notebook=False)



if __name__ == '__main__':
	run()