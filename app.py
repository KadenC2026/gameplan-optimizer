import numpy as np
import streamlit as st

# Define strategies
player_strategies = ["Serve Wide", "Serve T", "Approach Net", "Baseline Rally"]

# Example probabilities based on known tennis strategy outcomes in balanced matchups
# These can be calibrated with real data or player stats
strategy_effectiveness = {
    "Serve Wide": {"first_serve_win%": 0.68, "second_serve_win%": 0.52},
    "Serve T": {"first_serve_win%": 0.65, "second_serve_win%": 0.49},
    "Approach Net": {"net_point_win%": 0.62, "passing_shot_defense%": 0.4},
    "Baseline Rally": {"baseline_win%": 0.55, "error_rate": 0.15}
}

def compute_expected_value(strategy, serve_strength, baseline_consistency, opponent_defense):
    if strategy == "Serve Wide" or strategy == "Serve T":
        first_serve_ev = serve_strength * strategy_effectiveness[strategy]["first_serve_win%"]
        second_serve_ev = (1 - serve_strength) * strategy_effectiveness[strategy]["second_serve_win%"]
        return round(first_serve_ev + second_serve_ev, 3)
    elif strategy == "Approach Net":
        win_prob = strategy_effectiveness[strategy]["net_point_win%"] * (1 - opponent_defense)
        return round(win_prob, 3)
    elif strategy == "Baseline Rally":
        win_prob = strategy_effectiveness[strategy]["baseline_win%"] + 0.1 * (baseline_consistency - strategy_effectiveness[strategy]["error_rate"])
        return round(win_prob, 3)
    return 0.0

# Streamlit App
st.title("🎾 GamePlan Optimizer - Real-Time Strategy Advisor")
st.markdown("Estimate the optimal tennis strategy using real-world probabilities based on your style and your opponent’s tendencies.")

st.header("🧍 Your Player Profile")
serve_strength = st.slider("1st Serve Accuracy (%)", 0.0, 1.0, 0.65, 0.01)
baseline_consistency = st.slider("Baseline Rally Consistency (1 - Error Rate)", 0.0, 1.0, 0.85, 0.01)

st.header("🎯 Opponent Profile")
opponent_defense = st.slider("Opponent Net Defense Skill (0 = weak, 1 = strong)", 0.0, 1.0, 0.5, 0.01)

if st.button("📈 Suggest Optimal Strategy"):
    results = []
    for strategy in player_strategies:
        ev = compute_expected_value(strategy, serve_strength, baseline_consistency, opponent_defense)
        results.append((strategy, ev))

    sorted_results = sorted(results, key=lambda x: x[1], reverse=True)
    best_strategy, best_ev = sorted_results[0]

    st.success(f"**Best Strategy:** {best_strategy}")
    st.metric(label="Expected Point Win Probability", value=f"{best_ev:.2f}")

    st.subheader("All Strategies Evaluated:")
    for strat, val in sorted_results:
        st.write(f"- **{strat}**: {val:.2f}")
