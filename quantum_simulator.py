import networkx as nx
import matplotlib.pyplot as plt
import random

from network_topology import G, node_objects  # Uses pre-built nodes and graph

# --- Link Class Definition ---
class Link:
    def __init__(self, node1, node2, node_objects):
        type1 = node_objects[node1].node_type
        type2 = node_objects[node2].node_type

        self.nodes = (node1, node2)
        self.link_type = 'quantum' if type1 == 'quantum' and type2 == 'quantum' else 'classical'

        if self.link_type == 'quantum':
            self.distance = random.randint(10, 100)
            self.decoherence_rate = 0.01
            self.ent_swap_fail_prob = random.uniform(0.05, 0.2)
        else:
            self.latency = random.randint(10, 50)
            self.packet_loss_prob = 0.05

    def simulate_quantum(self):
        decoherence_prob = self.distance * self.decoherence_rate
        fail_decoherence = random.random() < decoherence_prob
        fail_ent_swap = random.random() < self.ent_swap_fail_prob
        success = not (fail_decoherence or fail_ent_swap)

        print(f"Quantum link {self.nodes[0]}-{self.nodes[1]}: "
              f"decoherence_prob={decoherence_prob:.2f}, "
              f"ent_swap_fail_prob={self.ent_swap_fail_prob:.2f}, success={success}")
        return success

    def simulate_classical(self):
        lost = random.random() < self.packet_loss_prob
        success = not lost
        print(f"Classical link {self.nodes[0]}-{self.nodes[1]}: "
              f"packet_loss_prob={self.packet_loss_prob:.2f}, "
              f"latency={self.latency}ms, success={success}")
        return success, self.latency

# --- Attach Link Objects to Graph Edges ---
for u, v in G.edges():
    link = Link(u, v, node_objects)
    G[u][v]['link'] = link
    G[u][v]['type'] = link.link_type  # for visualization

# --- Simulation Functions ---
def simulate_quantum_link(u, v, G):
    link = G[u][v]['link']
    if link.link_type != 'quantum':
        return None
    return link.simulate_quantum()

def simulate_classical_link(u, v, G):
    link = G[u][v]['link']
    if link.link_type != 'classical':
        return None
    return link.simulate_classical()

# --- Visualization ---
def visualize_network(G):
    pos = nx.spring_layout(G, seed=42)

    quantum_nodes = [n for n, d in G.nodes(data=True) if d['node_type'] == 'quantum']
    classical_nodes = [n for n, d in G.nodes(data=True) if d['node_type'] == 'classical']

    quantum_edges = [(u, v) for u, v, d in G.edges(data=True) if d['type'] == 'quantum']
    classical_edges = [(u, v) for u, v, d in G.edges(data=True) if d['type'] == 'classical']

    nx.draw_networkx_nodes(G, pos, nodelist=quantum_nodes, node_color='skyblue', node_size=700, label='Quantum')
    nx.draw_networkx_nodes(G, pos, nodelist=classical_nodes, node_color='orange', node_size=700, label='Classical')

    nx.draw_networkx_edges(G, pos, edgelist=quantum_edges, edge_color='green', width=2, label='Quantum Link')
    nx.draw_networkx_edges(G, pos, edgelist=classical_edges, edge_color='red', style='dashed', width=2, label='Classical Link')

    nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')
    plt.title("Hybrid Quantum-Classical Network")
    plt.legend()
    plt.axis('off')
    plt.tight_layout()
    plt.show()

# --- Run Simulations ---
print("\nSimulating Quantum Links:")
for u, v in G.edges():
    if G[u][v]['type'] == 'quantum':
        simulate_quantum_link(u, v, G)

print("\nSimulating Classical Links:")
for u, v in G.edges():
    if G[u][v]['type'] == 'classical':
        simulate_classical_link(u, v, G)

print("\nVisualizing Network:")
visualize_network(G)
