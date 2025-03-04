import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import random

st.title('Employee Productivity and Performance Influence Simulation')

# Parameters
num_employees = st.slider('Number of Employees', 10, 200, 100)
connection_prob = st.slider('Connection Probability', 0.01, 1.0, 0.1)
initial_high_performers = st.slider('Initial High Performers', 1, num_employees, 5)
time_steps = st.slider('Time Steps', 1, 100, 50)

# Initialize graph
G = nx.erdos_renyi_graph(num_employees, connection_prob)
for node in G.nodes:
    G.nodes[node]['status'] = 'neutral'

# Assign initial high performers
high_performers = random.sample(list(G.nodes), initial_high_performers)
for node in high_performers:
    G.nodes[node]['status'] = 'high_performer'

positive_influence_counts = []
engaged_counts = []
disengaged_counts = []

# Simulation
for t in range(time_steps):
    new_statuses = {}
    for node in G.nodes:
        neighbors = list(G.neighbors(node))
        high_performer_neighbors = sum(1 for n in neighbors if G.nodes[n]['status'] == 'high_performer')
        disengaged_neighbors = sum(1 for n in neighbors if G.nodes[n]['status'] == 'disengaged')
        
        if G.nodes[node]['status'] == 'neutral':
            if high_performer_neighbors > len(neighbors) * 0.3:
                new_statuses[node] = 'engaged'
            elif disengaged_neighbors > len(neighbors) * 0.3:
                new_statuses[node] = 'disengaged'
        elif G.nodes[node]['status'] == 'engaged':
            if disengaged_neighbors > len(neighbors) * 0.5:
                new_statuses[node] = 'disengaged'
        elif G.nodes[node]['status'] == 'disengaged':
            if high_performer_neighbors > len(neighbors) * 0.5:
                new_statuses[node] = 'engaged'
    
    for node, status in new_statuses.items():
        G.nodes[node]['status'] = status

    positive_influence_counts.append(sum(1 for n in G.nodes if G.nodes[n]['status'] == 'high_performer'))
    engaged_counts.append(sum(1 for n in G.nodes if G.nodes[n]['status'] == 'engaged'))
    disengaged_counts.append(sum(1 for n in G.nodes if G.nodes[n]['status'] == 'disengaged'))

# Plot time series
fig, ax = plt.subplots()
ax.plot(positive_influence_counts, color='red', label='High Performers')
ax.plot(engaged_counts, color='green', label='Engaged Employees')
ax.plot(disengaged_counts, color='blue', label='Disengaged Employees')
ax.set_title('📈 Employee Performance Dynamics Over Time')
ax.set_xlabel('Time Steps')
ax.set_ylabel('Number of Employees')
ax.legend()
st.pyplot(fig)

# Plot network
color_map = []
for node in G:
    if G.nodes[node]['status'] == 'high_performer':
        color_map.append('red')
    elif G.nodes[node]['status'] == 'neutral':
        color_map.append('gray')
    elif G.nodes[node]['status'] == 'engaged':
        color_map.append('green')
    elif G.nodes[node]['status'] == 'disengaged':
        color_map.append('blue')

fig, ax = plt.subplots()
nx.draw(G, node_color=color_map, with_labels=True, ax=ax)
ax.set_title('👥 Organizational Influence Network')
st.pyplot(fig)

st.markdown(
    """
    **Legend:**
    - 🔴 **High Performer** – Actively excelling and inspiring others.
    - ⚪ **Neutral** – Baseline performance, open to influence.
    - 🟢 **Engaged** – Sustained positive productivity.
    - 🔵 **Disengaged** – Experiencing reduced productivity.
    """
)
