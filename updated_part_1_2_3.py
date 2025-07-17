import networkx as nx
import matplotlib.pyplot as plt
import random
import copy

random.seed(42)

# ----------------- Node and Edge Setup -----------------
node_types = {
    'classical': ['A', 'B', 'C', 'D', 'E'],
    'quantum':   ['F', 'G', 'H', 'I', 'J']
}

G = nx.Graph()

for node in node_types['classical']:
    G.add_node(node, type='classical', entanglement_storage=False)
for node in node_types['quantum']:
    G.add_node(node, type='quantum', entanglement_storage=True)

edges = [
    ('A', 'B', 'classical'), ('B', 'C', 'classical'), ('C', 'D', 'classical'), ('D', 'E', 'classical'),
    ('F', 'G', 'quantum'), ('F', 'H', 'quantum'), ('G', 'H', 'quantum'), ('H', 'I', 'quantum'), ('I', 'J', 'quantum'),
    ('J', 'D', 'quantum'), ('B', 'I', 'quantum'), ('C', 'H', 'quantum'), ('E', 'J', 'quantum'),
    ('A', 'F', 'classical'), ('E', 'G', 'classical'), ('J', 'D', 'classical'), ('B', 'I', 'classical'),
    ('C', 'H', 'classical'), ('E', 'J', 'classical')
]

def get_channel_factor(channel_type):
    return {'amplitude': 1.0, 'phase': 0.7, 'depolarizing': 1.2}.get(channel_type, 1.0)

def compute_decoherence_rate(base, temp, env_noise, quality, typ):
    return max(
        base * (1 + 0.01 * temp) * (1 + 0.5 * env_noise) * get_channel_factor(typ) * (1 - 0.5 * quality), 0
    )

for u, v, kind in edges:
    if kind == 'quantum' and G.nodes[u]['type'] == 'quantum' and G.nodes[v]['type'] == 'quantum':
        base = 0.01
        temp = random.uniform(0.01, 4)
        noise = random.uniform(0, 1)
        quality = random.uniform(0.7, 0.99)
        typ = random.choice(['amplitude', 'phase', 'depolarizing'])
        deco = compute_decoherence_rate(base, temp, noise, quality, typ)
        G.add_edge(u, v,
            type='quantum', can_store_entanglement=True,
            distance=random.randint(10, 100),
            temperature=temp, env_noise=noise, qubit_quality=quality,
            channel_type=typ, decoherence_rate=deco,
            ent_swap_fail_prob=random.uniform(0.05, 0.2),
            memory_qubits=random.randint(4, 10)
        )
    else:
        G.add_edge(u, v,
            type='classical', can_store_entanglement=False,
            latency=random.randint(10, 50),
            packet_loss_prob=random.uniform(0.01, 0.1))

# ----------------- Simulators -----------------
def simulate_entanglement_swap(u, v, G):
    edge = G[u][v]
    if edge['type'] != 'quantum': return None
    decoherence_prob = edge['distance'] * edge['decoherence_rate']
    swap_fail_prob = edge['ent_swap_fail_prob']
    fail = random.random() < decoherence_prob or random.random() < swap_fail_prob
    print(f"  Entanglement swap {u}-{v} | deco={decoherence_prob:.2g}, swap_fail={swap_fail_prob:.2g} >>> {'FAIL' if fail else 'SUCCESS'}")
    return not fail

def simulate_classical_link(u, v, G):
    edge = G[u][v]
    if edge['type'] != 'classical': return None
    fail = random.random() < edge['packet_loss_prob']
    print(f"  Classical {u}-{v} | latency={edge['latency']}, loss={edge['packet_loss_prob']:.2g} >>> {'FAIL' if fail else 'SUCCESS'}")
    return not fail

def simulate_quantum_link(u, v, G):
    return simulate_entanglement_swap(u, v, G)

def simulate_quantum_edge_with_enhancements(G, u, v):
    edge = G[u][v]
    orig_deco = edge['decoherence_rate']
    orig_swap = edge['ent_swap_fail_prob']
    if edge['distance'] > 70:
        edge['decoherence_rate'] *= 0.5
        edge['ent_swap_fail_prob'] *= 0.5
    if edge['decoherence_rate'] > 0.2 or edge['ent_swap_fail_prob'] > 0.2:
        edge['decoherence_rate'] *= 0.3
        edge['ent_swap_fail_prob'] *= 0.3
    result = simulate_entanglement_swap(u, v, G)
    edge['decoherence_rate'] = orig_deco
    edge['ent_swap_fail_prob'] = orig_swap
    return result

# ----------------- Analysis -----------------
def baseline_quantum_success(G):
    total, success = 0, 0
    print("\n📊 Baseline Quantum Simulation:")
    for u, v in G.edges():
        if G[u][v]['type'] == 'quantum':
            total += 1
            if simulate_entanglement_swap(u, v, G): success += 1
    print(f"Baseline Success: {success}/{total} = {100*success/total:.2f}%")
    return 100 * success / total if total else 0

def simulate_with_enhancements(G):
    total, success = 0, 0
    print("\n📊 Enhanced Quantum Simulation:")
    for u, v in G.edges():
        if G[u][v]['type'] == 'quantum':
            total += 1
            if simulate_quantum_edge_with_enhancements(G, u, v): success += 1
    print(f"Enhanced Success: {success}/{total} = {100*success/total:.2f}%")
    return 100 * success / total if total else 0

def plot_comparison_chart(baseline, improved):
    plt.figure(figsize=(8, 5))
    bars = plt.bar(['Baseline', 'With Enhancements'], [baseline, improved], color=['red', 'green'])
    plt.ylim(0, 100)
    plt.ylabel("Success Rate (%)")
    for bar in bars:
        y = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, y + 1, f"{y:.2f}%", ha='center')
    plt.title("Quantum Link Success Comparison")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# ----------------- Visualization -----------------
def visualize_network(G):
    pos = nx.spring_layout(G, seed=42)
    q_nodes = [n for n, d in G.nodes(data=True) if d['type'] == 'quantum']
    c_nodes = [n for n, d in G.nodes(data=True) if d['type'] == 'classical']
    q_edges = [(u, v) for u, v, d in G.edges(data=True) if d['type'] == 'quantum']
    c_edges = [(u, v) for u, v, d in G.edges(data=True) if d['type'] == 'classical']
    nx.draw_networkx_nodes(G, pos, nodelist=q_nodes, node_color='skyblue', node_size=700)
    nx.draw_networkx_nodes(G, pos, nodelist=c_nodes, node_color='orange', node_size=700)
    nx.draw_networkx_edges(G, pos, edgelist=q_edges, edge_color='green', width=2)
    nx.draw_networkx_edges(G, pos, edgelist=c_edges, edge_color='red', width=2, style='dashed')
    nx.draw_networkx_labels(G, pos, font_size=12, font_weight='bold')
    plt.title("Hybrid Quantum-Classical Network")
    plt.axis('off')
    plt.show()

# ----------------- No-Cloning -----------------
def attempt_quantum_cloning(source, destinations, G):
    if len(destinations) > 1:
        print(f"\n❌ No-Cloning Violation: {source} → {destinations}")
        return False
    dest = destinations[0]
    if G.has_edge(source, dest) and G[source][dest]['type'] == 'quantum':
        print(f"\n✅ Quantum Transmission Allowed: {source} → {dest}")
        return simulate_quantum_link(source, dest, G)
    print(f"\n⚠️ Invalid: No quantum link from {source} to {dest}")
    return False

# ----------------- Main Execution -----------------
if __name__ == "__main__":
    print("\n📡 Quantum Links:")
    for u, v in G.edges():
        if G[u][v]['type'] == 'quantum':
            simulate_entanglement_swap(u, v, G)

    print("\n📡 Classical Links:")
    for u, v in G.edges():
        if G[u][v]['type'] == 'classical':
            simulate_classical_link(u, v, G)

    print("\n🛰️ Visualizing Network:")
    visualize_network(G)

    print("\n=== Quantum Repeater Simulation ===")
    baseline = baseline_quantum_success(G)
    improved = simulate_with_enhancements(G)
    print(f"\n🎯 Improvement: {improved - baseline:.2f}%")
    plot_comparison_chart(baseline, improved)

    print("\n--- Simulating No-Cloning ---")
    attempt_quantum_cloning('F', ['G'], G)
    attempt_quantum_cloning('F', ['G', 'H'], G)
    attempt_quantum_cloning('A', ['B'], G)
