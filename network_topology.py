import networkx as nx
import matplotlib.pyplot as plt
import random

# --- Node Class Definition ---
class Node:
    def __init__(self, name, node_type):
        self.name = name
        self.node_type = node_type
        self.can_store_entanglement = (node_type == 'quantum')
        self.memory_qubits = random.randint(4, 10) if node_type == 'quantum' else 0
        self.decoherence_rate = round(random.uniform(0.01, 0.1), 3) if node_type == 'quantum' else None
        self.processing_delay = random.randint(1, 10)

    def to_dict(self):
        return {
            'node_type': self.node_type,
            'can_store_entanglement': self.can_store_entanglement,
            'memory_qubits': self.memory_qubits,
            'decoherence_rate': self.decoherence_rate,
            'processing_delay': self.processing_delay
        }

# --- Fixed node list ---
quantum_nodes = ['A', 'C', 'E', 'G', 'I', 'K', 'M', 'O', 'Q']
classical_nodes = ['B', 'D', 'F', 'H', 'J', 'L', 'N', 'P', 'R']
all_nodes = quantum_nodes + classical_nodes

# --- Create Graph and Node Instances ---
G = nx.Graph()
node_objects = {}

for node_name in all_nodes:
    node_type = 'quantum' if node_name in quantum_nodes else 'classical'
    node_obj = Node(node_name, node_type)
    node_objects[node_name] = node_obj
    G.add_node(node_name, **node_obj.to_dict())

# --- Ensure connected graph, then add extra edges ---
edges = []
connected = set([all_nodes[0]])
while len(connected) < len(all_nodes):
    a = random.choice(list(connected))
    b = random.choice([n for n in all_nodes if n not in connected])
    G.add_edge(a, b)
    edges.append((a, b))
    connected.add(b)

# Add extra random edges
for _ in range(12):
    a, b = random.sample(all_nodes, 2)
    if not G.has_edge(a, b):
        G.add_edge(a, b)

# --- Visualization ---
pos = nx.spring_layout(G, seed=42)
plt.figure(figsize=(12, 8))

nx.draw_networkx_nodes(G, pos,
                       nodelist=quantum_nodes,
                       node_color='skyblue',
                       node_shape='o',
                       label='Quantum Nodes')

nx.draw_networkx_nodes(G, pos,
                       nodelist=classical_nodes,
                       node_color='lightcoral',
                       node_shape='s',
                       label='Classical Nodes')

nx.draw_networkx_edges(G, pos)
nx.draw_networkx_labels(G, pos, font_size=10)

plt.legend(scatterpoints=1)
plt.title("Hybrid Quantum-Classical Network (9 Quantum + 9 Classical)")
plt.axis('off')
plt.tight_layout()
plt.show()

# --- View Node Properties ---
print("\nNode Properties:")
for node_name in G.nodes():
    data = node_objects[node_name]
    print(f"{node_name}:")
    for key, value in data.to_dict().items():
        print(f"  {key}: {value}")
