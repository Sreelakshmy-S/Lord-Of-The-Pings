import networkx as nx
import matplotlib.pyplot as plt
import random

random.seed(42)  # For consistent results

# Define node types
node_types = {
    'classical': ['A', 'B', 'C', 'D', 'E'],
    'quantum': ['F', 'G', 'H', 'I', 'J']
}

G = nx.Graph()

# Add nodes
for node in node_types['classical']:
    G.add_node(node, type='classical', entanglement_storage=False)

for node in node_types['quantum']:
    G.add_node(node, type='quantum', entanglement_storage=True)

# Define edge list with physically valid links
edges = [
    ('A', 'B', 'classical'), 
    ('B', 'C', 'classical'),
    ('C', 'D', 'classical'),
    ('D', 'E', 'classical'),
    ('F', 'G', 'quantum'),
    ('F', 'H', 'quantum'),
    ('G', 'H', 'quantum'),
    ('H', 'I', 'quantum'),
    ('I', 'J', 'quantum'),
    ('J', 'D', 'quantum'),
    ('B', 'I', 'quantum'),
    ('C', 'H', 'quantum'),
    ('E', 'J', 'quantum'),
    ('A', 'F', 'classical'),
    ('E', 'G', 'classical'),
    ('J', 'D', 'classical'),
    ('B', 'I', 'classical'),
    ('C', 'H', 'classical'),
    ('E', 'J', 'classical')
]

# Add edges with proper attributes
for u, v, link_type in edges:
    if link_type == 'quantum':
        if G.nodes[u]['type'] == 'quantum' and G.nodes[v]['type'] == 'quantum':
            G.add_edge(u, v,
                       type='quantum',
                       distance=random.randint(10, 100),
                       decoherence_rate=0.01,
                       ent_swap_fail_prob=random.uniform(0.05, 0.2),
                       environment_noise=random.uniform(0.1, 0.4),
                       fiber_quality_factor=random.uniform(0.7, 1.0),
                       temperature_factor=random.uniform(0.5, 1.5))
        else:
            G.add_edge(u, v,
                       type='classical',
                       latency=random.randint(10, 50),
                       packet_loss_prob=random.uniform(0.01, 0.1))
    else:
        G.add_edge(u, v,
                   type='classical',
                   latency=random.randint(10, 50),
                   packet_loss_prob=random.uniform(0.01, 0.1))

# ------------------ Simulation Functions ------------------ #

def simulate_quantum_link(u, v, G):
    edge = G[u][v]
    if edge['type'] != 'quantum':
        return None

    decoherence_prob = (
        edge['distance'] * edge['decoherence_rate'] *
        edge['environment_noise'] *
        (1 - edge['fiber_quality_factor']) *
        edge['temperature_factor']
    )

    ent_swap_fail = edge['ent_swap_fail_prob']
    failed_decoherence = random.random() < decoherence_prob
    failed_ent_swap = random.random() < ent_swap_fail
    success = not (failed_decoherence or failed_ent_swap)

    print(f"Quantum link {u}-{v}: distance={edge['distance']} km, "
          f"decoherence_prob={decoherence_prob:.3f}, "
          f"ent_swap_fail_prob={ent_swap_fail:.2f}, success={success}")
    print(f"   [EnvNoise={edge['environment_noise']:.2f}, FiberQual={edge['fiber_quality_factor']:.2f}, "
          f"Temp={edge['temperature_factor']:.2f}]")
    return success

def simulate_classical_link(u, v, G):
    edge = G[u][v]
    if edge['type'] != 'classical':
        return None

    latency = edge['latency']
    packet_loss_prob = edge['packet_loss_prob']
    lost = random.random() < packet_loss_prob
    success = not lost

    print(f"Classical link {u}-{v}: latency={latency}ms, "
          f"packet_loss_prob={packet_loss_prob:.2f}, success={success}")
    return success, latency

# ------------------ Visualization ------------------ #

def visualize_network(G):
    pos = nx.spring_layout(G, seed=42)

    quantum_nodes = [n for n, d in G.nodes(data=True) if d['type'] == 'quantum']
    classical_nodes = [n for n, d in G.nodes(data=True) if d['type'] == 'classical']
    quantum_edges = [(u, v) for u, v, d in G.edges(data=True) if d['type'] == 'quantum']
    classical_edges = [(u, v) for u, v, d in G.edges(data=True) if d['type'] == 'classical']

    nx.draw_networkx_nodes(G, pos, nodelist=quantum_nodes, node_color='skyblue', node_size=700, label='Quantum Node')
    nx.draw_networkx_nodes(G, pos, nodelist=classical_nodes, node_color='orange', node_size=700, label='Classical Node')
    nx.draw_networkx_edges(G, pos, edgelist=quantum_edges, edge_color='green', width=2, label='Quantum Link')
    nx.draw_networkx_edges(G, pos, edgelist=classical_edges, edge_color='red', width=2, style='dashed', label='Classical Link')
    nx.draw_networkx_labels(G, pos, font_size=12, font_weight='bold')

    plt.title("Enhanced Hybrid Quantum-Classical Network (No Interference)")
    plt.axis('off')
    plt.legend()
    plt.show()

# ------------------ Hybrid Routing Protocol ------------------ #

def hybrid_route(source, target, G):
    print(f"\n🚦 Hybrid Routing: Trying to send from {source} to {target}")

    def path_success(path):
        for u, v in zip(path, path[1:]):
            edge = G[u][v]
            if edge['type'] == 'quantum':
                if not simulate_quantum_link(u, v, G):
                    print(f"❌ Quantum link failed: {u} -> {v}")
                    return False, (u, v)
            else:
                success, _ = simulate_classical_link(u, v, G)
                if not success:
                    print(f"❌ Classical link failed: {u} -> {v}")
                    return False, (u, v)
        return True, None

    # Try quantum-only path
    if G.nodes[source]['type'] == 'quantum' and G.nodes[target]['type'] == 'quantum':
        try:
            q_path = nx.shortest_path(G, source=source, target=target)
            if all(G[u][v]['type'] == 'quantum' for u, v in zip(q_path, q_path[1:])):
                print(f"🔬 Trying quantum-only path: {' -> '.join(q_path)}")
                success, failed_link = path_success(q_path)
                if success:
                    print("✅ Message sent successfully over quantum path.")
                    return q_path
        except Exception:
            pass

    # Fallback hybrid path
    temp_graph = G.copy()
    attempts = 0
    max_attempts = 5
    while attempts < max_attempts:
        try:
            path = nx.shortest_path(temp_graph, source=source, target=target)
            print(f"🔁 Attempting hybrid path: {' -> '.join(path)}")
            success, failed_link = path_success(path)
            if success:
                print("✅ Message sent successfully over hybrid path.")
                return path
            else:
                temp_graph.remove_edge(*failed_link)
                print(f"🔁 Retrying without failed link: {failed_link}")
                attempts += 1
        except nx.NetworkXNoPath:
            print("❌ No more alternate paths available.")
            break

    print("❌ Message delivery failed after multiple attempts.")
    return None

# ------------------ Run Simulations ------------------ #

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

print("\n🚀 Testing Hybrid Routing from A to J:")
path1 = hybrid_route('A', 'J', G)
print(f"Final path: {path1}")

print("\n🚀 Testing Hybrid Routing from F to J:")
path2 = hybrid_route('F', 'J', G)
print(f"Final path: {path2}")
