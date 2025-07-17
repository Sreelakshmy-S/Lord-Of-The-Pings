import networkx as nx
import matplotlib.pyplot as plt
import random
import numpy as np

# --- Define node types ---
node_types = {
    'classical': ['A', 'B', 'C', 'D', 'E'],
    'quantum': ['F', 'G', 'H', 'I', 'J']
}

# --- Create Graph ---
G = nx.Graph()

# Add nodes
for node in node_types['classical']:
    G.add_node(node, type='classical', entanglement_storage=False)

for node in node_types['quantum']:
    G.add_node(node, type='quantum', entanglement_storage=True, qubits = random.uniform(4,10))

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

# Add edges with appropriate attributes
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

# --- Baseline Quantum Success Rate ---
def baseline_quantum_success(G):
    success_rates = []
    for u, v, data in G.edges(data=True):
        if data['type'] == 'quantum':
            distance = data['distance']
            decoherence = data['decoherence_rate']
            fiber_quality = data['fiber_quality_factor']
            noise = data['environment_noise']
            temp = data['temperature_factor']
            # Example success rate function
            rate = (fiber_quality / (1 + decoherence * distance)) * np.exp(-noise * temp)
            success_rates.append(rate)
    return np.mean(success_rates) * 100  # convert to percentage

# --- Simulation with Enhancements ---
def simulate_with_enhancements(G):
    G_enhanced = G.copy()
    added_repeaters = []

    for u, v, data in G.edges(data=True):
        if data['type'] == 'quantum':
            # Criteria for bottleneck
            if data['distance'] > 60 or data['fiber_quality_factor'] < 0.8:
                # Insert virtual repeater node
                new_node = f"{u}_{v}_repeater"
                added_repeaters.append(new_node)
                G_enhanced.add_node(new_node, type='quantum', entanglement_storage=True)

                # Remove old edge and add two new links
                G_enhanced.remove_edge(u, v)
                for x, y in [(u, new_node), (new_node, v)]:
                    G_enhanced.add_edge(x, y,
                        type='quantum',
                        distance=data['distance'] / 2,
                        decoherence_rate=data['decoherence_rate'] / 2,
                        ent_swap_fail_prob=data['ent_swap_fail_prob'] * 0.8,  # improved with repeater
                        environment_noise=data['environment_noise'] * 0.8,
                        fiber_quality_factor=min(1.0, data['fiber_quality_factor'] * 1.1),
                        temperature_factor=max(0.5, data['temperature_factor'] * 0.9))
    return baseline_quantum_success(G_enhanced)

# --- Plot Comparison Chart ---
def plot_comparison_chart(baseline, improved):
    labels = ['Baseline', 'With Quantum Repeaters']
    values = [baseline, improved]

    plt.figure(figsize=(7, 5))
    bars = plt.bar(labels, values, color=['skyblue', 'lightgreen'])
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + 0.25, yval + 1, f'{yval:.2f}%', fontsize=12)

    plt.title("Quantum Link Success Rate Improvement")
    plt.ylabel("Average Success Rate (%)")
    plt.ylim(0, 100)
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.show()

# --- Run Simulation ---
print("\n=== Quantum Repeater Simulation ===") 
baseline_rate = baseline_quantum_success(G)
improved_rate = simulate_with_enhancements(G)
print(f"\n🎯 Baseline Success Rate: {baseline_rate:.2f}%")
print(f"🚀 Improved Success Rate: {improved_rate:.2f}%")
print(f"✅ Improvement: {improved_rate - baseline_rate:.2f}%")

plot_comparison_chart(baseline_rate, improved_rate)
