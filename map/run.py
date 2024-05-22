import yaml
from pyvis.network import Network


def is_def(node_id): return 'D' in node_id
def is_axiom(node_id): return 'A' in node_id
def is_prop(node_id): return 'P' in node_id
def is_cor(node_id): return 'c' in node_id
def is_schol(node_id): return 's' in node_id


def run():

	with open("./logical.yaml") as fs:
		graph = yaml.safe_load(fs)
	with open("./text-en-curley.yaml") as fs:
		text = yaml.safe_load(fs)

	net = Network(directed=True)

	for node_id in graph.keys():
		
		if is_def(node_id):     color = '#EC7063'
		elif is_axiom(node_id): color = '#52BE80'
		elif is_prop(node_id):
			if is_cor(node_id): color = '#AED6F1'
			else:               color = '#2E86C1'

		if is_cor(node_id) or is_schol(node_id): description = ""
		else:                                    description = text[node_id]

		net.add_node(node_id, label=node_id, title=description, shape='dot', color=color)
		
		parent_ids = graph[node_id]
		if parent_ids is None:   continue
		if len(parent_ids) == 0: continue

		# Ignore references to scholia  ##
		parent_ids = [pid for pid in parent_ids if not is_schol(pid)]

		for parent_id in parent_ids:
			net.add_edge(parent_id, node_id)

	net.toggle_physics(True)
	net.show('ethica_map.html', notebook=False)



if __name__ == '__main__':
	run()