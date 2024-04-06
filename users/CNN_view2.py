import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Initialize plot
fig, ax = plt.subplots(figsize=(10, 6))
ax.set_xlim(-1, 14)
ax.set_ylim(0, 10)
plt.axis('off')

# Network configuration and node positions
layers = [5, 4, 3, 2, 1]  # Number of nodes in each layer
layer_positions = np.linspace(0, 12, len(layers))  # X positions of the layers
node_positions = {0: np.linspace(1, 9, layers[0])}
for i in range(1, len(layers)):
    prev_layer_nodes = node_positions[i-1]
    node_positions[i] = [(prev_layer_nodes[n] + prev_layer_nodes[n+1]) / 2 for n in range(layers[i-1]-1)]

# Draw static parts of the network
def draw_network():
    for i, pos in enumerate(layer_positions):
        y = node_positions[i]
        ax.scatter([pos]*len(y), y, color='skyblue', edgecolor='black', zorder=5)
        if i > 0:
            for start_y in node_positions[i-1]:
                for end_y in node_positions[i]:
                    ax.plot([layer_positions[i-1], pos], [start_y, end_y], 'grey', linewidth=0.5, zorder=1)
draw_network()

# Calculate total "ping" actions
total_pings = sum(len(node_positions[i-1]) * len(node_positions[i]) for i in range(1, len(layers)))

# Animation update function
def update(frame):
    current_ping = frame % total_pings  # Current ping number
    for i in range(1, len(layers)):
        layer_pings = len(node_positions[i-1]) * len(node_positions[i])
        if current_ping < layer_pings:
            src_idx = current_ping // len(node_positions[i])
            dst_idx = current_ping % len(node_positions[i])
            src_x, src_y = layer_positions[i-1], node_positions[i-1][src_idx]
            dst_x, dst_y = layer_positions[i], node_positions[i][dst_idx]
            ax.plot([src_x, dst_x], [src_y, dst_y], color='skyblue', linewidth=2, zorder=3)
            break
        current_ping -= layer_pings

# Initialize and run the animation
ani = FuncAnimation(fig, update, frames=total_pings, interval=100, repeat=True)

plt.show()
