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
    # Classical ↔ Classical
    ('A', 'B', 'classical'), 
    ('B', 'C', 'classical'),
    ('C', 'D', 'classical'),
    ('D', 'E', 'classical'),

    # Quantum ↔ Quantum
    ('F', 'G', 'quantum'),
    ('F', 'H', 'quantum'),
    ('G', 'H', 'quantum'),
    ('H', 'I', 'quantum'),
    ('I', 'J', 'quantum'),
    ('J', 'D', 'quantum'),  # D is classical, so this will become classical
    ('B', 'I', 'quantum'),  # B is classical → convert to classical
    ('C', 'H', 'quantum'),  # C is classical → convert to classical
    ('E', 'J', 'quantum'),  # E is classical → convert to classical

    # Classical ↔ Quantum (should be classical links)
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
        # Ensure both nodes are quantum
        if G.nodes[u]['type'] == 'quantum' and G.nodes[v]['type'] == 'quantum':
            G.add_edge(u, v,
                       type='quantum',
                       can_store_entanglement = True,
                       distance=random.randint(10, 100),
                       decoherence_rate=0.01,
                       ent_swap_fail_prob=random.uniform(0.05, 0.2),
                       memory_qubits = random.randint(4, 10))
        else:
            # Convert invalid quantum link to classical
            G.add_edge(u, v,
                       type='classical',
                       can_store_entanglement = False,
                       latency=random.randint(10, 50),
                       packet_loss_prob=random.uniform(0.01, 0.1))
    else:  # classical
        G.add_edge(u, v,
                   type='classical',
                   can_store_entanglement = False,
                   latency=random.randint(10, 50),
                   packet_loss_prob=random.uniform(0.01, 0.1))
        
print("📌 Node Properties:")
for node in G.nodes(data=True):
    name, attributes = node
    print(f"Node {name}:")
    for key, value in attributes.items():
        print(f"  {key}: {value}")
    print()


# ------------------ Enhanced Quantum Simulation with Rerouting ------------------ #

REPEATER_DISTANCE_THRESHOLD = 70
REPEATER_EFFECTIVENESS = 0.5

QEC_THRESHOLD = 0.2
QEC_EFFECTIVENESS = 0.3

BOTTLENECK_TRAFFIC_THRESHOLD = 100
BOTTLENECK_WEIGHT = 1e6  # Effectively blocks high-traffic links in shortest_path

def baseline_quantum_success(G):
    successful = 0
    total = 0
    print("\n📊 Baseline Quantum Link Simulation (No Repeaters):")
    for u, v in G.edges():
        if G[u][v]['type'] == 'quantum':
            total += 1
            if simulate_quantum_link(u, v, G):
                successful += 1
    success_rate = successful / total * 100 if total > 0 else 0
    print(f"Baseline Success Rate: {success_rate:.2f}% ({successful}/{total})")
    return success_rate


def simulate_with_enhancements(G):
    successful_links = 0
    total_links = 0
    print("\n📊 Quantum Link Simulation With Repeaters + QEC + Bottleneck Detection + Rerouting:")

    for u, v in G.edges():
        edge = G[u][v]

        if edge['type'] != 'quantum':
            continue

        total_links += 1

        rerouted = False
        use_reroute = False

        # 🚨 Detect Bottleneck
        if 'traffic' in edge and edge['traffic'] > BOTTLENECK_TRAFFIC_THRESHOLD:
            print(f"🚨 Bottleneck detected on link {u}-{v} with traffic {edge['traffic']}")
            use_reroute = True

        # 🔁 Try rerouting
        if use_reroute:
            try:
                path = nx.shortest_path(
                    G,
                    source=u,
                    target=v,
                    weight=lambda a, b, e: BOTTLENECK_WEIGHT if e.get('traffic', 0) > BOTTLENECK_TRAFFIC_THRESHOLD else 1,
                )

                if len(path) > 2:
                    print(f"🔁 Rerouting around bottleneck: {' -> '.join(path)}")

                    rerouted = True
                    reroute_success = True
                    for i in range(len(path) - 1):
                        x, y = path[i], path[i + 1]
                        if G[x][y]['type'] != 'quantum':
                            continue
                        success = simulate_quantum_edge_with_enhancements(G, x, y)
                        if not success:
                            reroute_success = False
                            break

                    if reroute_success:
                        successful_links += 1
                        continue

            except nx.NetworkXNoPath:
                print(f"⚠️ No reroute path found between {u} and {v}, simulating original link.")

        # If not rerouted or failed, simulate original link
        success = simulate_quantum_edge_with_enhancements(G, u, v)
        if success:
            successful_links += 1

    success_rate = successful_links / total_links * 100 if total_links > 0 else 0
    print(f"Success Rate With Enhancements: {success_rate:.2f}% ({successful_links}/{total_links})")
    return success_rate


def simulate_quantum_edge_with_enhancements(G, u, v):
    edge = G[u][v]

    # Backup
    orig_deco = edge['decoherence_rate']
    orig_swap = edge['ent_swap_fail_prob']

    # Apply repeater
    if edge['distance'] > REPEATER_DISTANCE_THRESHOLD:
        edge['decoherence_rate'] *= REPEATER_EFFECTIVENESS
        edge['ent_swap_fail_prob'] *= REPEATER_EFFECTIVENESS

    # Apply QEC if needed
    if edge['decoherence_rate'] > QEC_THRESHOLD or edge['ent_swap_fail_prob'] > QEC_THRESHOLD:
        edge['decoherence_rate'] *= QEC_EFFECTIVENESS
        edge['ent_swap_fail_prob'] *= QEC_EFFECTIVENESS

    # Simulate
    success = simulate_quantum_link(u, v, G)

    # Restore
    edge['decoherence_rate'] = orig_deco
    edge['ent_swap_fail_prob'] = orig_swap

    return success


def plot_comparison_chart(baseline, improved):
    scenarios = ['Baseline', 'With Repeaters']
    success_rates = [baseline, improved]
    colors = ['red', 'green']
    plt.figure(figsize=(8, 5))
    bars = plt.bar(scenarios, success_rates, color=colors)
    plt.title("Quantum Link Success Rate Comparison")
    plt.ylabel("Success Rate (%)")
    plt.ylim(0, 100)
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 2, f'{yval:.2f}%', ha='center', fontsize=10)
    plt.tight_layout()
    plt.show()

# ------------------ Simulation Functions ------------------ #

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

    print(f"Quantum link {u}-{v}: distance={distance} km, "
          f"decoherence_prob={decoherence_prob:.2f}, "
          f"ent_swap_fail_prob={ent_swap_fail:.2f}, success={success}")

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

    plt.title("Fixed Hybrid Quantum-Classical Network")
    plt.axis('off')
    plt.legend()
    plt.show()

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
# ------------------ Hybrid Routing Protocol ------------------ #

def hybrid_route(source, target, G):
    print(f"\n🚦 Hybrid Routing: Trying to send from {source} to {target}")

    def path_success(path):
        """Simulates the given path, returns True if all links succeed."""
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

    # Step 1: Try quantum-only path
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

    # Step 2: Try hybrid fallback with recovery
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



print("\n🚀 Testing Hybrid Routing from A to J:")
path1 = hybrid_route('A', 'J', G)
print(f"Final path: {path1}")

print("\n🚀 Testing Hybrid Routing from F to J:")
path2 = hybrid_route('F', 'J', G)
print(f"Final path: {path2}")

print("\n=== Quantum Repeater Simulation ===")
baseline_rate = baseline_quantum_success(G)
improved_rate = simulate_with_enhancements(G)
print(f"\n🎯 Improvement: {improved_rate - baseline_rate:.2f}%")
plot_comparison_chart(baseline_rate, improved_rate)
