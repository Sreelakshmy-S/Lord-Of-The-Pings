import networkx as nx
import random
from network_topology import G, node_objects
from quantum_simulator import simulate_quantum_link, visualize_network
import matplotlib.pyplot as plt

# --- Constants ---
REPEATER_DISTANCE_THRESHOLD = 70  # Threshold for long-distance link
REPEATER_EFFECTIVENESS = 0.5      # Reduces decoherence and swap fail prob by 50%

# --- Modified Link Simulation With Repeaters ---
def simulate_with_repeaters(G):
    successful_links = 0
    total_links = 0

    print("\nSimulating Quantum Links with Repeaters:")
    for u, v in G.edges():
        edge = G[u][v]
        link = edge['link']

        if edge['type'] != 'quantum':
            continue

        total_links += 1
        if link.distance > REPEATER_DISTANCE_THRESHOLD:
            # Apply repeater correction
            original_decoherence = link.decoherence_rate
            original_swap_fail = link.ent_swap_fail_prob

            # Reduce both by repeater effectiveness
            link.decoherence_rate *= REPEATER_EFFECTIVENESS
            link.ent_swap_fail_prob *= REPEATER_EFFECTIVENESS

            success = link.simulate_quantum()

            # Restore original rates (non-destructive for re-use)
            link.decoherence_rate = original_decoherence
            link.ent_swap_fail_prob = original_swap_fail
        else:
            success = link.simulate_quantum()

        if success:
            successful_links += 1

    success_rate = successful_links / total_links * 100 if total_links > 0 else 0
    print(f"\nQuantum Link Success Rate with Repeaters: {success_rate:.2f}% ({successful_links}/{total_links})")
    return success_rate

def baseline_quantum_success(G):
    successful = 0
    total = 0
    print("\nBaseline Quantum Link Simulation (No Repeaters):")
    for u, v in G.edges():
        if G[u][v]['type'] == 'quantum':
            total += 1
            if simulate_quantum_link(u, v, G):
                successful += 1
    success_rate = successful / total * 100 if total > 0 else 0
    print(f"\nBaseline Quantum Link Success Rate: {success_rate:.2f}% ({successful}/{total})")
    return success_rate

if __name__ == "__main__":

    print("=== Quantum Repeater Simulation ===")

    print("\n[1] Baseline Network Simulation:")
    baseline_rate = baseline_quantum_success(G)

    print("\n[2] Network Simulation with Quantum Repeaters:")
    improved_rate = simulate_with_repeaters(G)

    improvement = improved_rate - baseline_rate
    print(f"\n🎯 Improvement with Repeaters: {improvement:.2f}%")

    print("\n[3] Visualizing Network:")
    visualize_network(G)

# --- Bar Chart for Comparison ---
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

plot_comparison_chart(baseline_rate, improved_rate)    