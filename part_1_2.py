import networkx as nx
import matplotlib.pyplot as plt
import random

random.seed(42)  # For reproducibility

# Define classical and quantum nodes
node_types = {
    'classical': ['A', 'B', 'C', 'D', 'E'],
    'quantum': ['F', 'G', 'H', 'I', 'J']
}

G = nx.Graph()

# Add classical nodes
for node in node_types['classical']:
    G.add_node(node, type='classical', entanglement_storage=False)

# Add quantum nodes
for node in node_types['quantum']:
    G.add_node(node, type='quantum', entanglement_storage=True)

# Define edges with link type
edges = [
    ('A', 'B', 'classical'), ('A', 'F', 'quantum'), ('B', 'C', 'classical'),
    ('C', 'D', 'classical'), ('D', 'E', 'classical'), ('E', 'G', 'quantum'),
    ('F', 'G', 'quantum'), ('F', 'H', 'quantum'), ('G', 'H', 'quantum'),
    ('H', 'I', 'quantum'), ('I', 'J', 'quantum'), ('J', 'D', 'quantum'),
    ('B', 'I', 'quantum'), ('C', 'H', 'quantum'), ('E', 'J', 'quantum')
]

# Add edge attributes
for u, v, link_type in edges:
    if link_type == 'quantum':
        G.add_edge(
            u, v,
            type='quantum',
            distance=random.randint(10, 100),         # Simulated distance in km
            decoherence_rate=0.01,                    # Probability per km
            ent_swap_fail_prob=random.uniform(0.05, 0.2)  # Random failure rate
        )
    else:
        G.add_edge(
            u, v,
            type='classical',
            latency=random.randint(10, 50),               # ms latency
            packet_loss_prob=random.uniform(0.01, 0.1)    # Random packet loss 1%-10%
        )

# ------------------ Simulation Functions ------------------

def simulate_quantum_link(u, v, G):
    """Simulate decoherence and entanglement swap failure on quantum links."""
    edge = G[u][v]
    if edge['type'] != 'quantum':
        return None

    distance = edge['distance']
    decoherence_prob = distance * edge['decoherence_rate']
    ent_swap_fail = edge['ent_swap_fail_prob']

    failed_decoherence = random.random() < decoherence_prob
    failed_ent_swap = random.random() < ent_swap_fail

    success = not (failed_decoherence or failed_ent_swap)

    print(f"Quantum link {u}-{v}: distance={distance}km, "
          f"decoherence_prob={decoherence_prob:.2f}, "
          f"ent_swap_fail_prob={ent_swap_fail:.2f}, success={success}")

    return success

def simulate_classical_link(u, v, G):
    """Simulate packet loss and latency on classical links."""
    edge = G[u][v]
    if edge['type'] != 'classical':
        return None

    packet_loss = random.random() < edge['packet_loss_prob']
    latency = edge['latency']

    success = not packet_loss

    print(f"Classical link {u}-{v}: latency={latency}ms, "
          f"packet_loss_prob={edge['packet_loss_prob']:.2f}, success={success}")

    return success, latency

# ------------------ Visualization ------------------

def visualize_network(G):
    """Draw the hybrid network with colored nodes and edges."""
    pos = nx.spring_layout(G, seed=42)  # consistent layout

    # Nodes by type
    quantum_nodes = [n for n, attr in G.nodes(data=True) if attr['type'] == 'quantum']
    classical_nodes = [n for n, attr in G.nodes(data=True) if attr['type'] == 'classical']

    nx.draw_networkx_nodes(G, pos, nodelist=quantum_nodes, node_color='skyblue', node_size=700, label='Quantum')
    nx.draw_networkx_nodes(G, pos, nodelist=classical_nodes, node_color='orange', node_size=700, label='Classical')

    # Edges by type
    quantum_edges = [(u, v) for u, v, attr in G.edges(data=True) if attr['type'] == 'quantum']
    classical_edges = [(u, v) for u, v, attr in G.edges(data=True) if attr['type'] == 'classical']

    nx.draw_networkx_edges(G, pos, edgelist=quantum_edges, edge_color='green', width=2, label='Quantum Link')
    nx.draw_networkx_edges(G, pos, edgelist=classical_edges, edge_color='red', style='dashed', width=2, label='Classical Link')

    nx.draw_networkx_labels(G, pos, font_size=12, font_weight='bold')

    plt.title("Hybrid Quantum-Classical Network Topology")
    plt.legend()
    plt.axis('off')
    plt.tight_layout()
    plt.show()

# ------------------ Run Simulation ------------------

print("\n📡 Simulating Quantum Links:")
for u, v in G.edges():
    if G[u][v]['type'] == 'quantum':
        simulate_quantum_link(u, v, G)

print("\n📡 Simulating Classical Links:")
for u, v in G.edges():
    if G[u][v]['type'] == 'classical':
        simulate_classical_link(u, v, G)

print("\n🛰️ Visualizing Network Topology:")
visualize_network(G)
