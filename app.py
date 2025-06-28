import numpy as np
import streamlit as st

# Define sample strategies and outcomes
player_strategies = ["Serve Wide", "Serve T", "Approach Net", "Baseline Rally"]
opponent_weaknesses = ["Backhand", "Low Balls", "Passing Shots", "Forehand"]

# Payoff matrix: expected win probability of each player strategy vs opponent weakness
# Rows: player strategies, Columns: opponent weaknesses
payoff_matrix = np.array([
    [0.7, 0.6, 0.4, 0.5],  # Serve Wide
    [0.6, 0.5, 0.3, 0.7],  # Serve T
    [0.4, 0.8, 0.6, 0.5],  # Approach Net
    [0.5, 0.4, 0.3, 0.6]   # Baseline Rally
])

def recommend_strategy(weakness_profile):
    """
    weakness_profile: list of floats representing opponent weaknesses [0 to 1]
    Each entry corresponds to the columns in payoff_matrix
    """
    # Convert weakness profile into a column vector
    weakness_vector = np.array(weakness_profile)
    # Compute expected values for each strategy
    expected_values = payoff_matrix @ weakness_vector
    # Select the best strategy
    best_index = np.argmax(expected_values)
    return player_strategies[best_index], expected_values[best_index]

# Streamlit Web App
st.title("🎾 GamePlan Optimizer")
st.markdown("Rate your opponent's weaknesses from 0 (not a weakness) to 1 (very weak).")

weakness_input = []
for w in opponent_weaknesses:
    val = st.slider(f"{w}", 0.0, 1.0, 0.5, 0.05)
    weakness_input.append(val)

if st.button("Suggest Optimal Strategy"):
    strategy, value = recommend_strategy(weakness_input)
    st.success(f"Recommended Strategy: **{strategy}**")
    st.metric(label="Expected Point Win Probability", value=f"{value:.2f}")
