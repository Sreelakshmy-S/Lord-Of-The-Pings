import networkx as nx
import matplotlib.pyplot as plt
import random

random.seed(42)  # For reproducibility

# Node types
node_types = {
    'classical': ['A', 'B', 'C', 'D', 'E'],
    'quantum': ['F', 'G', 'H', 'I', 'J']
}

G = nx.Graph()

# Add nodes with attributes
for node in node_types['classical']:
    G.add_node(node, type='classical', entanglement_storage=False)

for node in node_types['quantum']:
    G.add_node(node, type='quantum', entanglement_storage=True)

# Define edges (quantum or classical)
edges = [
    ('A', 'B', 'classical'), ('A', 'F', 'quantum'), ('B', 'C', 'classical'),
    ('C', 'D', 'classical'), ('D', 'E', 'classical'), ('E', 'G', 'quantum'),
    ('F', 'G', 'quantum'), ('F', 'H', 'quantum'), ('G', 'H', 'quantum'),
    ('H', 'I', 'quantum'), ('I', 'J', 'quantum'), ('J', 'D', 'quantum'),
    ('B', 'I', 'quantum'), ('C', 'H', 'quantum'), ('E', 'J', 'quantum')
]

# Add edges with attributes, including variable entanglement fail prob
for u, v, link_type in edges:
    if link_type == 'quantum':
        G.add_edge(
            u, v,
            type='quantum',
            distance=random.randint(10, 100),
            decoherence_rate=0.01,
            ent_swap_fail_prob=random.uniform(0.05, 0.2)  # 5% - 20%
        )
    else:
        G.add_edge(
            u, v,
            type='classical',
            latency=random.randint(10, 50),
            packet_loss_prob=0.05
        )

# Simulation functions
def simulate_quantum_link(u, v, G):
    edge = G[u][v]
    if edge['type'] != 'quantum':
        return None

    distance = edge['distance']
    decoherence_prob = distance * edge['decoherence_rate']
    ent_swap_fail = edge['ent_swap_fail_prob']

    failed_decoherence = random.random() < decoherence_prob
    failed_ent_swap = random.random() < ent_swap_fail

    success = not (failed_decoherence or failed_ent_swap)

    print(f"Quantum link {u}-{v}: decoherence_prob={decoherence_prob:.2f}, "
          f"ent_swap_fail_prob={ent_swap_fail:.2f}, success={success}")

    return success

def simulate_classical_link(u, v, G):
    edge = G[u][v]
    if edge['type'] != 'classical':
        return None

    packet_loss = random.random() < edge['packet_loss_prob']
    latency = edge['latency']

    success = not packet_loss

    print(f"Classical link {u}-{v}: packet_loss_prob={edge['packet_loss_prob']}, "
          f"latency={latency}ms, success={success}")

    return success, latency

# Visualization function
def visualize_network(G):
    pos = nx.spring_layout(G, seed=42)  # fixed layout for consistency

    # Nodes: quantum blue, classical orange
    quantum_nodes = [n for n, attr in G.nodes(data=True) if attr['type'] == 'quantum']
    classical_nodes = [n for n, attr in G.nodes(data=True) if attr['type'] == 'classical']

    nx.draw_networkx_nodes(G, pos, nodelist=quantum_nodes, node_color='skyblue', node_size=700, label='Quantum')
    nx.draw_networkx_nodes(G, pos, nodelist=classical_nodes, node_color='orange', node_size=700, label='Classical')

    # Edges: quantum green, classical red
    quantum_edges = [(u, v) for u, v, attr in G.edges(data=True) if attr['type'] == 'quantum']
    classical_edges = [(u, v) for u, v, attr in G.edges(data=True) if attr['type'] == 'classical']

    nx.draw_networkx_edges(G, pos, edgelist=quantum_edges, edge_color='green', width=2, label='Quantum Link')
    nx.draw_networkx_edges(G, pos, edgelist=classical_edges, edge_color='red', style='dashed', width=2, label='Classical Link')

    nx.draw_networkx_labels(G, pos, font_size=12, font_weight='bold')

    plt.title("Hybrid Quantum-Classical Network Topology")
    plt.legend(scatterpoints=1)
    plt.axis('off')
    plt.show()

# Run simulation and visualization
print("\nSimulating Quantum Links:")
for u, v in G.edges():
    if G[u][v]['type'] == 'quantum':
        simulate_quantum_link(u, v, G)

print("\nSimulating Classical Links:")
for u, v in G.edges():
    if G[u][v]['type'] == 'classical':
        simulate_classical_link(u, v, G)

print("\nVisualizing network topology:")
visualize_network(G)
