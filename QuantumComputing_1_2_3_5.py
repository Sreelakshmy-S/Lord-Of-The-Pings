import networkx as nx
import matplotlib.pyplot as plt
import random

random.seed(42)  # For consistent results

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
            'type': self.node_type,
            'entanglement_storage': self.can_store_entanglement
        }


# --- Link Class Definition ---
class Link:
    def __init__(self, node1, node2, node_objects):
        type1 = node_objects[node1].node_type
        type2 = node_objects[node2].node_type
        self.nodes = (node1, node2)
        self.link_type = 'quantum' if type1 == 'quantum' and type2 == 'quantum' else 'classical'
        self.traffic = 0

        if self.link_type == 'quantum':
            self.distance = random.randint(10, 100)
            self.decoherence_rate = 0.01
            self.ent_swap_fail_prob = random.uniform(0.05, 0.2)
        else:
            self.latency = random.randint(10, 50)
            self.packet_loss_prob = random.uniform(0.01, 0.1)

    def simulate_quantum(self):
        decoherence_prob = self.distance * self.decoherence_rate
        fail_decoherence = random.random() < decoherence_prob
        fail_ent_swap = random.random() < self.ent_swap_fail_prob
        success = not (fail_decoherence or fail_ent_swap)

        print(f"Quantum link {self.nodes[0]}-{self.nodes[1]}: decoherence_prob={decoherence_prob:.2f}, "
              f"ent_swap_fail_prob={self.ent_swap_fail_prob:.2f}, success={success}")
        return success

    def simulate_classical(self):
        lost = random.random() < self.packet_loss_prob
        success = not lost
        print(f"Classical link {self.nodes[0]}-{self.nodes[1]}: "
              f"packet_loss_prob={self.packet_loss_prob:.2f}, latency={self.latency}ms, success={success}")
        return success, self.latency


# --- Network Setup ---
node_types = {
    'classical': ['A', 'B', 'C', 'D', 'E'],
    'quantum': ['F', 'G', 'H', 'I', 'J']
}

edges = [
    ('A', 'B', 'classical'), ('B', 'C', 'classical'), ('C', 'D', 'classical'), ('D', 'E', 'classical'),
    ('F', 'G', 'quantum'), ('F', 'H', 'quantum'), ('G', 'H', 'quantum'), ('H', 'I', 'quantum'),
    ('I', 'J', 'quantum'), ('J', 'D', 'quantum'), ('B', 'I', 'quantum'), ('C', 'H', 'quantum'),
    ('E', 'J', 'quantum'), ('A', 'F', 'classical'), ('E', 'G', 'classical'), ('J', 'D', 'classical'),
    ('B', 'I', 'classical'), ('C', 'H', 'classical'), ('E', 'J', 'classical')
]

G = nx.Graph()
node_objects = {}
link_objects = {}

# Add nodes
for ntype, names in node_types.items():
    for name in names:
        node = Node(name, ntype)
        node_objects[name] = node
        G.add_node(name, **node.to_dict())

# Print node properties
print("\n📌 Node Properties:")
for name, node in node_objects.items():
    print(f"Node {name}: type={node.node_type}, entanglement_storage={node.can_store_entanglement}, "
          f"memory_qubits={node.memory_qubits}, decoherence_rate={node.decoherence_rate}, "
          f"processing_delay={node.processing_delay}")

# Add edges
for u, v, link_type in edges:
    link = Link(u, v, node_objects)
    link_objects[(u, v)] = link
    link_objects[(v, u)] = link

    if link.link_type == 'quantum':
        G.add_edge(u, v,
                   type='quantum',
                   distance=link.distance,
                   decoherence_rate=link.decoherence_rate,
                   ent_swap_fail_prob=link.ent_swap_fail_prob)
    else:
        G.add_edge(u, v,
                   type='classical',
                   latency=link.latency,
                   packet_loss_prob=link.packet_loss_prob)

# --- Simulation Functions ---
def simulate_quantum_link(u, v):
    return link_objects[(u, v)].simulate_quantum()

def simulate_classical_link(u, v):
    return link_objects[(u, v)].simulate_classical()

# --- Routing Functions ---
def hybrid_route(source, target):
    print(f"\n\n🚦 Hybrid Routing: Trying to send from {source} to {target}")

    def path_success(path):
        for u, v in zip(path, path[1:]):
            edge_type = G[u][v]['type']
            if edge_type == 'quantum':
                if not simulate_quantum_link(u, v):
                    print(f"❌ Quantum link failed: {u} -> {v}")
                    return False, (u, v)
            else:
                success, _ = simulate_classical_link(u, v)
                if not success:
                    print(f"❌ Classical link failed: {u} -> {v}")
                    return False, (u, v)
        return True, None

    # Try quantum-only path first
    if node_objects[source].node_type == 'quantum' and node_objects[target].node_type == 'quantum':
        try:
            q_path = nx.shortest_path(G, source=source, target=target)
            if all(G[u][v]['type'] == 'quantum' for u, v in zip(q_path, q_path[1:])):
                print(f"🔬 Trying quantum-only path: {' -> '.join(q_path)}")
                success, _ = path_success(q_path)
                if success:
                    print("✅ Message sent successfully over quantum path.")
                    return q_path
        except:
            pass

    # Hybrid fallback
    attempts = 0
    temp_graph = G.copy()
    while attempts < 5:
        try:
            path = nx.shortest_path(temp_graph, source=source, target=target)
            print(f"🔁 Attempting hybrid path: {' -> '.join(path)}")
            success, failed = path_success(path)
            if success:
                print("✅ Message sent successfully over hybrid path.")
                return path
            else:
                temp_graph.remove_edge(*failed)
                print(f"🔁 Retrying without failed link: {failed}")
                attempts += 1
        except nx.NetworkXNoPath:
            print("❌ No more alternate paths available.")
            break

    print("❌ Message delivery failed after multiple attempts.")
    return None

# --- Visualize ---
def visualize_network():
    pos = nx.spring_layout(G, seed=42)
    quantum_nodes = [n for n, d in G.nodes(data=True) if d['type'] == 'quantum']
    classical_nodes = [n for n, d in G.nodes(data=True) if d['type'] == 'classical']
    quantum_edges = [(u, v) for u, v, d in G.edges(data=True) if d['type'] == 'quantum']
    classical_edges = [(u, v) for u, v, d in G.edges(data=True) if d['type'] == 'classical']

    nx.draw_networkx_nodes(G, pos, nodelist=quantum_nodes, node_color='skyblue', node_size=700, label='Quantum')
    nx.draw_networkx_nodes(G, pos, nodelist=classical_nodes, node_color='orange', node_size=700, label='Classical')
    nx.draw_networkx_edges(G, pos, edgelist=quantum_edges, edge_color='green', width=2)
    nx.draw_networkx_edges(G, pos, edgelist=classical_edges, edge_color='red', style='dashed', width=2)
    nx.draw_networkx_labels(G, pos, font_size=12, font_weight='bold')
    plt.title("Hybrid Quantum-Classical Network")
    plt.axis('off')
    plt.legend()
    plt.show()

# --- Run ---
print("\n📡 Simulating Quantum Links:")
for u, v in G.edges():
    if G[u][v]['type'] == 'quantum':
        simulate_quantum_link(u, v)

print("\n📡 Simulating Classical Links:")
for u, v in G.edges():
    if G[u][v]['type'] == 'classical':
        simulate_classical_link(u, v)

print("\n🛰️ Visualizing Network Topology:")
visualize_network()

print("\n🚀 Testing Hybrid Routing from A to J:")
path1 = hybrid_route('A', 'J')
print(f"Final path: {path1}")

print("\n🚀 Testing Hybrid Routing from F to J:")
path2 = hybrid_route('F', 'J')
print(f"Final path: {path2}")
