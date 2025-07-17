class Node:
    def __init__(self, name, node_type='classical'):
        self.name = name
        self.node_type = node_type  # 'quantum' or 'classical'
        self.can_store_entanglement = node_type == 'quantum'
        self.memory_qubits = 5 if node_type == 'quantum' else 0
        self.connections = []
import networkx as nx
import matplotlib.pyplot as plt

# Create a graph
G = nx.Graph()

# Define node types manually or randomly
node_types = {
    'A': 'quantum', 'B': 'classical', 'C': 'quantum', 'D': 'classical',
    'E': 'quantum', 'F': 'quantum', 'G': 'classical', 'H': 'classical',
    'I': 'quantum', 'J': 'classical'
}

# Add nodes with attributes
for node, n_type in node_types.items():
    G.add_node(node, node_type=n_type)

# Add edges
edges = [('A', 'B'), ('B', 'C'), ('C', 'D'), ('D', 'E'),
         ('E', 'F'), ('F', 'G'), ('G', 'H'), ('H', 'I'),
         ('I', 'J'), ('A', 'J'), ('C', 'F'), ('D', 'G')]
G.add_edges_from(edges)

pos = nx.spring_layout(G, seed=42)

# Draw nodes
quantum_nodes = [n for n, attr in G.nodes(data=True) if attr['node_type'] == 'quantum']
classical_nodes = [n for n, attr in G.nodes(data=True) if attr['node_type'] == 'classical']

nx.draw_networkx_nodes(G, pos, nodelist=quantum_nodes, node_color='skyblue', node_shape='o', label='Quantum')
nx.draw_networkx_nodes(G, pos, nodelist=classical_nodes, node_color='lightcoral', node_shape='s', label='Classical')

# Draw edges and labels
nx.draw_networkx_edges(G, pos)
nx.draw_networkx_labels(G, pos)
plt.legend(scatterpoints=1)
plt.title("Hybrid Quantum-Classical Network Topology")
plt.axis('off')
plt.show()
