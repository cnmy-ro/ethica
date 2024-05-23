import yaml
from pyvis.network import Network
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

np.random.seed(0)


# ---
# Config

TOPDOWN_LAYOUT = True


# ---
# Utils

def is_def(node_id):    return 'D' in node_id
def is_axiom(node_id):  return 'A' in node_id and 'Aff' not in node_id
def is_post(node_id):   return 'Post' in node_id
def is_prop(node_id):   return 'P' in node_id and 'Post' not in node_id
def is_lemma(node_id):  return 'L' in node_id
def is_cor(node_id):    return 'C' in node_id
def is_schol(node_id):  return 'S' in node_id
def is_affect(node_id): return 'Aff' in node_id
def get_part(node_id):  return int(node_id[0])


def init_graph():

	with open("./logical.yaml") as fs:
		logical_graph = yaml.safe_load(fs)
	with open("./text-en-curley.yaml") as fs:
		text = yaml.safe_load(fs)
	
	graph = nx.DiGraph()

	for node_id in logical_graph.keys():		
		if is_cor(node_id) or is_schol(node_id): description = ""
		else:                                    description = text[node_id]
		graph.add_node(node_id, label=node_id, title=description)
		parent_ids = logical_graph[node_id]
		if parent_ids is None:   continue
		if len(parent_ids) == 0: continue
		parent_ids = [pid for pid in parent_ids if not is_schol(pid)] # Ignore references to scholia  ##
		for parent_id in parent_ids:
			graph.add_edge(parent_id, node_id)

	return graph

	
def update_node_levels(graph):

	def get_bottom_most_parent_level_of_this_part(node_id, part, offset):
		parent_ids = graph.predecessors(node_id)
		parent_ids = [pid for pid in parent_ids if not is_schol(pid)]  # ignore scholia
		bottom_most_parent_level = 1
		for pid in parent_ids:
			if get_part(pid) != part:
				continue
			parent_level = graph.nodes[pid]['level'] - offset
			if parent_level > bottom_most_parent_level:
				bottom_most_parent_level = parent_level
		return bottom_most_parent_level

	def get_bottom_most_level_of_prev_part(part):
		offset = 1
		for node_id in graph.nodes:
			if get_part(node_id) != part - 1:
				continue
			if graph.nodes[node_id]['level'] > offset:
				offset = graph.nodes[node_id]['level']
		return offset
	
	part_offsets = {1:0, 2:None, 3:None, 4:None, 5:None}
	for node_id in graph.nodes:
		part = get_part(node_id)
		if part > 1 and part_offsets[part] is None:
			offset = get_bottom_most_level_of_prev_part(part)
		else:
			offset = part_offsets[part]

		if is_def(node_id) or is_axiom(node_id) or is_post(node_id):
			level = 1
		elif is_prop(node_id) or is_cor(node_id) or is_lemma(node_id) or is_affect(node_id):
			bottom_most_parent_level = get_bottom_most_parent_level_of_this_part(node_id, part, offset)
			level = bottom_most_parent_level + 1		
		
		graph.nodes[node_id]['level'] = offset + level		
	return graph


def update_node_pos(graph):

	node_pos = {}

	max_level = max([graph.nodes[node_id]['level'] for node_id in graph.nodes])

	ring_counter = 1
	for level in range(1, max_level):
		radius = 50 * ring_counter
		node_list = [node_id for node_id in graph.nodes if graph.nodes[node_id]['level'] == level]
		angle_offset = np.random.uniform(-np.pi, np.pi) # for stylistic purpose
		angles = np.linspace(-np.pi, np.pi, len(node_list)) + angle_offset
		xs, ys = radius * np.cos(angles), radius * np.sin(angles)
		for i, node_id in enumerate(node_list):
			graph.nodes[node_id]['x'] = xs[i]
			graph.nodes[node_id]['y'] = ys[i]
			graph.nodes[node_id]['physics'] = False
		if len(node_list) > 0:
			ring_counter += 1

	return graph


def update_node_style_attrs(graph):
	for node_id in graph.nodes:
		if is_def(node_id):
			color = '#EC7063'
		elif is_axiom(node_id) or is_post(node_id):
			color = '#52BE80'
		elif is_prop(node_id) or is_lemma(node_id):
			if is_cor(node_id): 
				color = '#AED6F1'
			else:
				color = '#2E86C1'
		elif is_affect(node_id):
			color = '#F1C40F'
		graph.nodes[node_id]['color'] = color
		graph.nodes[node_id]['shape'] = 'circle'
	return graph


def run():

	# Build graph
	graph = init_graph()
	graph = update_node_levels(graph)
	graph = update_node_pos(graph)
	graph = update_node_style_attrs(graph)

	# Show graph
	net = Network(directed=True, layout=TOPDOWN_LAYOUT, neighborhood_highlight=True)
	net.from_nx(graph)
	net.show('ethica_map.html', notebook=False)


# ---
# Run

if __name__ == '__main__':
	run()