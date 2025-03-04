import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import random
import time
import networkx as nx

# Initialize simulation parameters
def get_model_params():
    return {
        "N": st.sidebar.slider("Number of Employees", 50, 500, 100),
        "initial_high_performers": st.sidebar.slider("Initial High Performers", 1, 10, 3),
        "influence_probability": st.sidebar.slider("Influence Probability", 0.0, 1.0, 0.5),
        "retention_rate": st.sidebar.slider("Retention Rate", 0.0, 1.0, 0.7),
        "steps": st.sidebar.slider("Simulation Duration (Seconds)", 5, 100, 50),
    }

# Moving Average for smoothing
def moving_average(data, window_size=10):
    if len(data) < window_size:
        return data
    return np.convolve(data, np.ones(window_size)/window_size, mode='valid')

# Employee class
class Employee:
    def __init__(self, unique_id, status, influence_score):
        self.unique_id = unique_id
        self.status = status  # "high_performer", "neutral", "disengaged"
        self.influence_score = influence_score

    def influence(self, neighbors, influence_probability):
        if self.status == "high_performer":
            for neighbor in neighbors:
                if neighbor.status == "neutral":
                    if random.random() < (influence_probability * self.influence_score):
                        neighbor.status = "high_performer"
                elif neighbor.status == "disengaged":
                    if random.random() < (influence_probability * self.influence_score * 0.5):
                        neighbor.status = "neutral"
        elif self.status == "disengaged":
            for neighbor in neighbors:
                if neighbor.status == "neutral":
                    if random.random() < (influence_probability * 0.3):
                        neighbor.status = "disengaged"

# Organization Model
class OrganizationModel:
    def __init__(self, **params):
        self.num_employees = params["N"]
        self.influence_probability = params["influence_probability"]
        self.retention_rate = params["retention_rate"]
        self.G = nx.barabasi_albert_graph(self.num_employees, 3)
        self.employees = {}

        all_nodes = list(self.G.nodes())
        initial_high_performers = random.sample(all_nodes, params["initial_high_performers"])

        for node in all_nodes:
            influence_score = random.uniform(0.5, 1.5)
            status = "high_performer" if node in initial_high_performers else "neutral"
            self.employees[node] = Employee(node, status, influence_score)

        self.node_positions = nx.spring_layout(self.G)
        self.high_performer_counts = []
        self.disengaged_counts = []

    def step(self):
        for node, employee in self.employees.items():
            neighbors = [self.employees[n] for n in self.G.neighbors(node)]
            employee.influence(neighbors, self.influence_probability)

        for employee in self.employees.values():
            if employee.status == "high_performer":
                if random.random() > self.retention_rate:
                    employee.status = "disengaged"

        high_performers = sum(1 for e in self.employees.values() if e.status == "high_performer")
        disengaged = sum(1 for e in self.employees.values() if e.status == "disengaged")

        self.high_performer_counts.append(high_performers)
        self.disengaged_counts.append(disengaged)

# Visualization
def plot_organization(G, employees, positions, high_performer_counts, disengaged_counts):
    color_map = {"high_performer": "green", "neutral": "gray", "disengaged": "red"}
    node_colors = [color_map[employees[node].status] for node in G.nodes()]
    node_sizes = [employees[node].influence_score * 100 for node in G.nodes()]

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    nx.draw(G, pos=positions, ax=axes[0], node_color=node_colors, node_size=node_sizes, edge_color="lightgray")
    axes[0].set_title("Employee Influence Network")

    axes[1].plot(moving_average(high_performer_counts), color="green", label="High Performers")
    axes[1].plot(moving_average(disengaged_counts), color="red", label="Disengaged")
    axes[1].set_title("Performance Over Time")
    axes[1].set_xlabel("Time (Steps)")
    axes[1].set_ylabel("Number of Employees")
    axes[1].legend()

    plt.tight_layout()
    return fig

# Streamlit App
st.title("Employee Productivity and Performance Influence Simulation")
params = get_model_params()

if st.button("Run Simulation"):
    model = OrganizationModel(**params)
    progress_bar = st.progress(0)
    visual_plot = st.empty()

    for step_num in range(1, params["steps"] + 1):
        model.step()
        progress_bar.progress(step_num / params["steps"])
        fig = plot_organization(model.G, model.employees, model.node_positions, model.high_performer_counts, model.disengaged_counts)
        visual_plot.pyplot(fig)

    st.success("Simulation Complete.")

st.markdown(
    """
    ### Employee Productivity and Performance Influence Simulation

    This simulation explores how employee performance evolves through mentorship and influence in an organization.
    
    - **Green:** High-performing employees
    - **Gray:** Neutral employees
    - **Red:** Disengaged employees

    Adjust parameters like influence probability and retention rate to observe organizational dynamics.
    """
)
