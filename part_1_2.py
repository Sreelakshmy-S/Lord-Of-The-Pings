import networkx as nx
import matplotlib.pyplot as plt
import random

# Set random seed for reproducibility
random.seed(42)

# 1. Create Hybrid Network Graph
G = nx.Graph()

# Define node types
node_types = {
    'classical': ['A', 'B', 'C', 'D', 'E'],
    'quantum': ['F', 'G', 'H', 'I', 'J']
}

# Add nodes with attributes
for node in node_types['classical']:
    G.add_node(node, type='classical', entanglement_storage=False)

for node in node_types['quantum']:
    G.add_node(node, type='quantum', entanglement_storage=True)

# Define edges with type and attach properties
edges = [
    ('A', 'B', 'classical'), ('A', 'F', 'quantum'), ('B', 'C', 'classical'),
    ('C', 'D', 'classical'), ('D', 'E', 'classical'), ('E', 'G', 'quantum'),
    ('F', 'G', 'quantum'), ('F', 'H', 'quantum'), ('G', 'H', 'quantum'),
    ('H', 'I', 'quantum'), ('I', 'J', 'quantum'), ('J', 'D', 'quantum'),
    ('B', 'I', 'quantum'), ('C', 'H', 'quantum'), ('E', 'J', 'quantum')
]

# Add edges with attributes
for u, v, link_type in edges:
    if link_type == 'quantum':
        G.add_edge(u, v, type='quantum', 
                   distance=random.randint(10, 100),  # km
                   decoherence_rate=0.01,             # prob/km
                   ent_swap_fail_prob=0.1)            # prob of failure
    else:
        G.add_edge(u, v, type='classical', 
                   latency=random.randint(10, 50),     # ms
                   packet_loss_prob=0.05)              # 5% loss

# 2. Simulation Functions

def simulate_quantum_link_transmission(u, v, G):
    edge = G[u][v]
    if edge['type'] != 'quantum':
        return None
    
    distance = edge['distance']
    decoherence_prob = distance * edge['decoherence_rate']
    ent_swap_fail = edge['ent_swap_fail_prob']
    
    failed_decoherence = random.random() < decoherence_prob
    failed_ent_swap = random.random() < ent_swap_fail
    
    success = not (failed_decoherence or failed_ent_swap)
    
    print(f"Quantum link {u}-{v}: distance={distance}, "
          f"decoherence_prob={decoherence_prob:.2f}, "
          f"ent_swap_fail_prob={ent_swap_fail}, success={success}")
    
    return success

def simulate_classical_link_transmission(u, v, G):
    edge = G[u][v]
    if edge['type'] != 'classical':
        return None
    
    packet_loss = random.random() < edge['packet_loss_prob']
    latency = edge['latency']
    
    success = not packet_loss
    
    print(f"Classical link {u}-{v}: packet_loss_prob={edge['packet_loss_prob']}, "
          f"latency={latency}ms, success={success}")
    
    return success, latency

# 3. No-Cloning Check Function

def attempt_quantum_cloning(source, destinations):
    if len(destinations) > 1:
        print(f"\n❌ No-Cloning Violation: Attempted to send quantum state from {source} to multiple destinations {destinations}")
        return False
    else:
        dest = destinations[0]
        if G.has_edge(source, dest) and G[source][dest]['type'] == 'quantum':
            print(f"\n✅ Quantum state transmission from {source} to {dest} allowed (no cloning)")
            return simulate_quantum_link_transmission(source, dest, G)
        else:
            print(f"\n⚠️ No valid quantum link between {source} and {dest}")
            return False

# 4. Visualize the Network
pos = nx.spring_layout(G, seed=42)
colors = ['blue' if G.nodes[node]['type'] == 'classical' else 'green' for node in G.nodes]
labels = {node: f"{node} ({'Q' if G.nodes[node]['type'] == 'quantum' else 'C'})" for node in G.nodes}

plt.figure(figsize=(10, 7))
nx.draw(G, pos, with_labels=True, labels=labels, node_color=colors, node_size=1000, font_size=10)
plt.title("Hybrid Quantum-Classical Network Topology")
plt.show()

# 5. Run Simulations

print("\n--- Simulating Quantum Links ---")
for u, v in G.edges():
    if G[u][v]['type'] == 'quantum':
        simulate_quantum_link_transmission(u, v, G)

print("\n--- Simulating Classical Links ---")
for u, v in G.edges():
    if G[u][v]['type'] == 'classical':
        simulate_classical_link_transmission(u, v, G)

print("\n--- Testing No-Cloning Scenarios ---")
# Valid: sending to one destination
attempt_quantum_cloning('F', ['G'])

# Invalid: trying to copy quantum state
attempt_quantum_cloning('F', ['G', 'H'])

# Invalid: classical link, should warn
attempt_quantum_cloning('A', ['B'])
