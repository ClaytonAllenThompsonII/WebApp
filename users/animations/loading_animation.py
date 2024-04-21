import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Initialize plot
fig, ax = plt.subplots(figsize=(10, 6))
ax.set_xlim(-1, 16)  # Extended space for visual clarity
ax.set_ylim(0, 10)
ax.set_facecolor("#f0f0f0")
plt.axis('off')

# Network configuration with adjusted layers
layers = [8, 5, 3, 2, 1]  # Number of nodes per layer
layer_positions = np.linspace(0, 12, len(layers))  # Horizontal positions of layers

# Calculate node positions
node_positions = {}
for i, num_nodes in enumerate(layers):
    if i == 0:
        node_positions[i] = np.linspace(2, 8, num_nodes)
    elif i == 1:
        node_positions[i] = np.linspace(node_positions[0][0] + 0.75, node_positions[0][-1] - 0.75, num_nodes)
    elif i == 2:
        node_positions[i] = [node_positions[1][n] for n in range(1, 4)]
    elif i == 3:
        node_positions[i] = [(node_positions[2][0] + node_positions[2][1]) / 2, (node_positions[2][1] + node_positions[2][2]) / 2]
    else:
        node_positions[i] = [(node_positions[3][0] + node_positions[3][1]) / 2]

# Function to draw the network
def draw_network():
    for i, x_pos in enumerate(layer_positions):
        y_positions = node_positions[i]
        color = 'skyblue' if i < len(layers) - 1 else 'lightgreen'
        size = 120 if i == 0 else 100
        ax.scatter([x_pos] * len(y_positions), y_positions, color=color, edgecolor='black', s=size, zorder=5)

draw_network()  # Initial drawing of the network

# Collect all possible pings for the animation, starting from top nodes down in each layer
pings = []
for i in range(len(layers) - 1):
    for start_pos in reversed(node_positions[i]):  # Reverse to start pinging from bottom to top in the source layer
        for end_pos in reversed(node_positions[i + 1]):  # Reverse to ensure we go top to bottom in the target layer
            pings.append(((layer_positions[i], start_pos), (layer_positions[i + 1], end_pos)))

# Animation update function to include pinging effect
def update(frame): 
    # Draw up to the current frame
    draw_network()  # Redraw static parts to ensure visibility
    for i, ((x1, y1), (x2, y2)) in enumerate(pings[:frame + 1]):
        color = 'lightblue' if i < frame else 'lightgreen'  # Previous pings turn black, current ping is red
        ax.plot([x1, x2], [y1, y2], color=color, linewidth=1.3, zorder=3)

# Initialize and run the animation
ani = FuncAnimation(fig, update, frames=len(pings), interval=10, repeat=False)

plt.show()
