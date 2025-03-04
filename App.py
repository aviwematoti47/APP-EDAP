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
        "steps": st.sidebar.slider("Simulation Duration (Seconds)", 5, 100, 50),
    }

def moving_average(data, window_size=10):
    if len(data) < window_size:
        return data
    return np.convolve(data, np.ones(window_size)/window_size, mode='valid')

class Employee:
    def __init__(self, unique_id, status, capacity):
        self.unique_id = unique_id
        self.status = status  # "high_performer", "neutral", "engaged", "disengaged"
        self.capacity = capacity  # Determines influence susceptibility
        self.influence_timer = 0
        self.engagement_timer = 0

    def interact(self, colleagues, influence_probability):
        if self.status == "high_performer":
            for colleague in colleagues:
                if colleague.status == "neutral":
                    susceptibility_factor = 1.0 / colleague.capacity
                    if random.random() < (influence_probability * susceptibility_factor):
                        colleague.influence_timer = self.capacity

    def update_status(self):
        if self.status == "neutral" and self.influence_timer > 0:
            self.influence_timer -= 1
            if self.influence_timer == 0:
                self.status = "high_performer"
                self.engagement_timer = 3
        elif self.status == "high_performer" and self.engagement_timer > 0:
            self.engagement_timer -= 1
            if self.engagement_timer == 0:
                self.status = "engaged" if random.random() > 0.5 else "disengaged"

class PerformanceInfluenceModel:
    def __init__(self, **params):
        self.num_employees = params["N"]
        self.influence_probability = params["influence_probability"]
        self.G = nx.barabasi_albert_graph(self.num_employees, 3)
        self.employees = {}

        all_nodes = list(self.G.nodes())
        initial_high_performers = random.sample(all_nodes, params["initial_high_performers"])

        for node in all_nodes:
            capacity = random.choice([1, 2, 3, 4])
            status = "high_performer" if node in initial_high_performers else "neutral"
            self.employees[node] = Employee(node, status, capacity)

        self.node_positions = nx.spring_layout(self.G)
        self.history = []
        self.influence_counts = []
        self.engaged_counts = []
        self.disengaged_counts = []

    def step(self, step_num):
        influences = 0
        newly_engaged = 0
        newly_disengaged = 0

        for node, employee in self.employees.items():
            colleagues = [self.employees[n] for n in self.G.neighbors(node)]
            employee.interact(colleagues, self.influence_probability)

        for employee in self.employees.values():
            prev_status = employee.status
            employee.update_status()
            if prev_status == "neutral" and employee.status == "high_performer":
                influences += 1
            elif prev_status == "high_performer" and employee.status == "engaged":
                newly_engaged += 1
            elif prev_status == "high_performer" and employee.status == "disengaged":
                newly_disengaged += 1

        self.influence_counts.append(influences)
        self.engaged_counts.append(newly_engaged)
        self.disengaged_counts.append(newly_disengaged)
        self.history.append({node: employee.status for node, employee in self.employees.items()})

def plot_visuals(G, employees, positions, influences, engaged_counts, disengaged_counts):
    color_map = {"high_performer": "gold", "neutral": "gray", "engaged": "green", "disengaged": "red"}
    node_colors = [color_map[employees[node].status] for node in G.nodes()]
    node_sizes = [employees[node].capacity * 50 for node in G.nodes()]

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    nx.draw(G, pos=positions, ax=axes[0, 0], node_color=node_colors, with_labels=False, node_size=node_sizes, edge_color="gray")
    axes[0, 0].set_title("Employee Influence Network")

    axes[0, 1].plot(moving_average(influences), color="gold", linewidth=1.5)
    axes[0, 1].set_title("Influence Spread Over Time")
    axes[0, 1].set_xlabel("Time (Seconds)")
    axes[0, 1].set_ylabel("New Influences per Step")

    axes[1, 0].plot(moving_average(engaged_counts), color="green", linewidth=1.5)
    axes[1, 0].set_title("New Engaged Per Step")
    axes[1, 0].set_xlabel("Time (Seconds)")
    axes[1, 0].set_ylabel("Engaged Count Per Step")

    axes[1, 1].plot(moving_average(disengaged_counts), color="red", linewidth=1.5)
    axes[1, 1].set_title("New Disengaged Per Step")
    axes[1, 1].set_xlabel("Time (Seconds)")
    axes[1, 1].set_ylabel("Disengaged Count Per Step")

    plt.tight_layout()
    return fig

st.title("Employee Productivity and Performance Influence Simulation")
params = get_model_params()

if st.button("Run Simulation"):
    st.markdown("<script>window.scrollTo(0, document.body.scrollHeight);</script>", unsafe_allow_html=True)
    model = PerformanceInfluenceModel(**params)
    progress_bar = st.progress(0)
    visual_plot = st.empty()

    for step_num in range(1, params["steps"] + 1):
        model.step(step_num)
        progress_bar.progress(step_num / params["steps"])
        fig = plot_visuals(model.G, model.employees, model.node_positions, model.influence_counts, model.engaged_counts, model.disengaged_counts)
        visual_plot.pyplot(fig)

    st.write("Simulation Complete.")
st.markdown(
    """
    ## Employee Productivity and Performance Influence Simulation

    This simulation models **employee performance influence** within an organization using a **scale-free network**. 
    In this network:
    
    - **Nodes** represent employees.
    - **Edges** represent relationships (mentorship, team collaboration, etc.).
    
    ### How it Works:
    - **High-performing employees (red nodes)** influence their direct connections.
    - **Neutral employees (gray nodes)** can become high performers through peer influence.
    - After a period of high performance, employees either:
        - Remain **engaged and productive (green nodes)** or
        - Become **disengaged (blue nodes)** due to factors like burnout or negative culture.
    - The **retention rate** affects the likelihood that engaged employees stay productive.
    - The **influence score** measures how strongly an employee can impact others based on their connections.

    ### Parameters you can adjust:
    - **Number of Employees (Agents)**: Total number of people in the organization.
    - **Initial High Performers**: How many start as high performers.
    - **Influence Probability**: How likely high performance spreads between connected employees.
    - **Experiment Duration**: How long the simulation runs.

    ### Visualizations:
    - **Network Graph** (Top-Left): See how employees influence each other in real-time.
    - **Influence Over Time** (Top-Right): Number of new high performers at each step.
    - **Engaged Employees Over Time** (Bottom-Left): Number of employees staying engaged.
    - **Disengaged Employees Over Time** (Bottom-Right): Number of employees losing engagement.

    ### Purpose:
    This model helps explore how **positive influence, retention, and disengagement** spread through an organization, 
    providing insights into how workplace culture and performance may evolve over time.

    Adjust the parameters on the sidebar and run the simulation to see how influence dynamics play out in your organization!
    """
)
