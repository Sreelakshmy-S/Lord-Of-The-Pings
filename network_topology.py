import networkx as nx
import matplotlib.pyplot as plt
import random

# --- Fixed node list ---
quantum_nodes = ['A', 'C', 'E', 'G', 'I', 'K', 'M', 'O', 'Q']
classical_nodes = ['B', 'D', 'F', 'H', 'J', 'L', 'N', 'P', 'R']
all_nodes = quantum_nodes + classical_nodes

# --- Create graph ---
G = nx.Graph()

# --- Add nodes with fixed attributes ---
for node in quantum_nodes:
    G.add_node(node,
               node_type='quantum',
               can_store_entanglement=True,
               memory_qubits=random.randint(4, 10),
               decoherence_rate=round(random.uniform(0.01, 0.1), 3),
               processing_delay=random.randint(1, 10))

for node in classical_nodes:
    G.add_node(node,
               node_type='classical',
               can_store_entanglement=False,
               memory_qubits=0,
               decoherence_rate=None,
               processing_delay=random.randint(1, 10))

# --- Ensure connected graph, then add extra edges ---
edges = []
connected = set([all_nodes[0]])
while len(connected) < len(all_nodes):
    a = random.choice(list(connected))
    b = random.choice([n for n in all_nodes if n not in connected])
    G.add_edge(a, b)
    edges.append((a, b))
    connected.add(b)

# Add extra edges randomly
for _ in range(12):
    a, b = random.sample(all_nodes, 2)
    if not G.has_edge(a, b):
        G.add_edge(a, b)

# --- Visualize the network ---
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

# --- View node properties ---
print("\nNode Properties:")
for node, data in G.nodes(data=True):
    print(f"{node}:")
    for key, value in data.items():
        print(f"  {key}: {value}")
