# tennis_tracker_streamlit.py
import streamlit as st
import datetime

# Initialize session state
if "match_started" not in st.session_state:
    st.session_state.match_started = False
    st.session_state.stats = {
        "Player 1": {"points": 0, "aces": 0, "winners": 0, "unforced": 0, "forced": 0, "rally_0_4": 0, "rally_5_8": 0, "rally_9+": 0},
        "Player 2": {"points": 0, "aces": 0, "winners": 0, "unforced": 0, "forced": 0, "rally_0_4": 0, "rally_5_8": 0, "rally_9+": 0}
    }

# Match Setup
if not st.session_state.match_started:
    st.title("🎾 Tennis Match Tracker")
    st.subheader("Match Setup")
    col1, col2 = st.columns(2)
    with col1:
        player1 = st.text_input("Player 1", value="Player 1")
    with col2:
        player2 = st.text_input("Player 2", value="Player 2")

    server = st.selectbox("Who is serving first?", [player1, player2])
    surface = st.selectbox("Surface", ["Hard", "Clay", "Grass"])
    court_type = st.selectbox("Court Type", ["Indoor", "Outdoor"])
    temp = st.slider("Temperature (°F)", 40, 110, 70)
    humidity = st.slider("Humidity (%)", 0, 100, 50)
    match_type = st.radio("Scoring Format", ["Full 3 Sets", "10-Point Tiebreak for 3rd Set"])
    ads = st.checkbox("No-Ad Scoring")

    if st.button("Start Match"):
        st.session_state.player1 = player1
        st.session_state.player2 = player2
        st.session_state.server = server
        st.session_state.match_started = True
        st.experimental_rerun()

# Match In Progress
else:
    p1 = st.session_state.player1
    p2 = st.session_state.player2
    st.title(f"{p1} vs {p2}")
    st.caption(f"Date: {datetime.date.today()} | Surface: {surface}, {court_type} | Temp: {temp}°F | Humidity: {humidity}%")

    st.header("Current Point")
    rally_len = st.slider("Rally Length", 0, 100, 4)
    point_winner = st.radio("Who won the point?", [p1, p2], horizontal=True)
    point_type = st.radio("Point Type", ["Ace", "Winner", "Unforced Error", "Forced Error"], horizontal=True)

    if st.button("Log Point"):
        stats = st.session_state.stats
        rally_bucket = "rally_0_4" if rally_len <= 4 else "rally_5_8" if rally_len <= 8 else "rally_9+"

        stats[point_winner]["points"] += 1
        stats[point_winner][rally_bucket] += 1

        if point_type == "Ace":
            stats[point_winner]["aces"] += 1
        elif point_type == "Winner":
            stats[point_winner]["winners"] += 1
        elif point_type == "Unforced Error":
            stats[point_winner]["unforced"] += 1
        elif point_type == "Forced Error":
            stats[point_winner]["forced"] += 1

        st.success(f"Point for {point_winner} logged successfully.")

    st.header("Live Stats")
    for player in [p1, p2]:
        with st.expander(player):
            s = st.session_state.stats[player]
            st.metric("Total Points Won", s["points"])
            st.write(f"Aces: {s['aces']}, Winners: {s['winners']}, UE: {s['unforced']}, FE: {s['forced']}")
            st.write(f"Rally 0-4: {s['rally_0_4']}, 5-8: {s['rally_5_8']}, 9+: {s['rally_9+']}")

    if st.button("End Match and Get AI Feedback"):
        p1_stats = st.session_state.stats[p1]
        p2_stats = st.session_state.stats[p2]

        def get_feedback(stats):
            fb = ""
            if stats["rally_9+"] > stats["rally_0_4"]:
                fb += "Try to end points sooner. "
            if stats["unforced"] > stats["winners"]:
                fb += "Reduce unforced errors. "
            if stats["aces"] == 0:
                fb += "Work on serve variety for more free points."
            return fb or "Solid performance overall!"

        st.subheader("AI Feedback")
        st.markdown(f"**{p1}:** {get_feedback(p1_stats)}")
        st.markdown(f"**{p2}:** {get_feedback(p2_stats)}")
