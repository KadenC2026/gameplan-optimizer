# tennis_match_app.py
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Tennis Match Tracker", layout="wide")

# ========== Helper Functions ==========
def format_score(score):
    points = ["0", "15", "30", "40", "Ad"]
    return points[min(score, 4)]

def get_next_server(current_server, is_doubles):
    return (current_server + 1) % (4 if is_doubles else 2)

def get_set_winner(sets):
    p1_sets = sum(1 for s in sets.values() if s[0] > s[1])
    p2_sets = sum(1 for s in sets.values() if s[1] > s[0])
    return 0 if p1_sets > p2_sets else 1 if p2_sets > p1_sets else None

# ========== Session Initialization ==========
def init():
    st.session_state.update({
        "match_started": False,
        "players": [],
        "teams": {},
        "is_doubles": False,
        "scoring": {},
        "conditions": {},
        "current_set": 1,
        "sets": {1: [0, 0], 2: [0, 0], 3: [0, 0]},
        "games": [0, 0],
        "points": [0, 0],
        "server": 0,
        "point_log": [],
        "stats": {i: {
            "aces": 0, "dfs": 0, "winners": 0, "ue": 0, "fe": 0,
            "1st_serves": 0, "1st_won": 0, "2nd_serves": 0, "2nd_won": 0,
            "bp_faced": 0, "bp_saved": 0,
            "returns_1st": [0, 0], "returns_2nd": [0, 0],
            "bp_won": 0, "bp_total": 0,
            "tpw": 0, "rally_0_4": 0, "rally_5_8": 0, "rally_9+": 0
        } for i in range(2)},
        "rally_length": 0,
        "point_result": None,
        "shot_detail": None,
        "net_approach": [False, False]
    })

if "match_started" not in st.session_state:
    init()

# ========== Match Setup ==========
if not st.session_state.match_started:
    st.title("🎾 Tennis Match Tracker - Match Setup")

    st.subheader("Match Type")
    is_doubles = st.toggle("Doubles Match")
    st.session_state.is_doubles = is_doubles

    with st.form("setup_form"):
        col1, col2 = st.columns(2)
        with col1:
            if is_doubles:
                p1 = st.text_input("Team 1 - Player 1", "Player 1")
                p2 = st.text_input("Team 1 - Player 2", "Player 2")
                st.session_state.players = [p1 + " & " + p2, ""]
            else:
                p1 = st.text_input("Player 1", "Player 1")
                st.session_state.players = [p1, ""]

        with col2:
            if is_doubles:
                p3 = st.text_input("Team 2 - Player 1", "Player 3")
                p4 = st.text_input("Team 2 - Player 2", "Player 4")
                st.session_state.players[1] = p3 + " & " + p4
            else:
                p2 = st.text_input("Player 2", "Player 2")
                st.session_state.players[1] = p2

        server = st.selectbox("Who serves first?", st.session_state.players)
        surface = st.selectbox("Surface", ["Hard", "Clay", "Grass"])
        speed = st.selectbox("Court Speed", ["Slow", "Medium", "Fast"])
        indoor = st.selectbox("Court Type", ["Indoor", "Outdoor"])
        temp = st.slider("Temperature", 40, 110, 75)
        humidity = st.slider("Humidity", 0, 100, 50)
        ads = st.toggle("No-Ad Scoring")
        third_set = st.radio("Third Set Format", ["Full Set", "10-Point Tiebreak"])

        submitted = st.form_submit_button("Start Match")
        if submitted:
            st.session_state.server = st.session_state.players.index(server)
            st.session_state.conditions = {
                "surface": surface, "speed": speed, "type": indoor,
                "temp": temp, "humidity": humidity
            }
            st.session_state.scoring = {"ads": ads, "third": third_set}
            st.session_state.match_started = True
            st.rerun()

# ========== Match UI ==========
else:
    p1, p2 = st.session_state.players
    server = st.session_state.server

    st.title(f"📅 {datetime.now().strftime('%B %d, %Y')}")
    st.subheader(f"Set {st.session_state.current_set} | {p1}: {st.session_state.sets[st.session_state.current_set][0]} - {p2}: {st.session_state.sets[st.session_state.current_set][1]}")
    st.markdown(f"## 🎾 Game Score: **{format_score(st.session_state.points[0])} - {format_score(st.session_state.points[1])}**")
    st.markdown(f"🟡 Server: **{st.session_state.players[server]}**")

    with st.form("log_point"):
        st.radio("Serve type", ["First", "Second"], key="serve")
        st.slider("Rally Length", 0, 100, key="rally_length")
        col1, col2 = st.columns(2)
        with col1:
            st.checkbox(f"{p1} net approach", key="net_p1")
        with col2:
            st.checkbox(f"{p2} net approach", key="net_p2")

        winner = st.radio("Who won the point?", [p1, p2], key="winner")
        result = st.radio("How was point won?", ["Ace", "Winner", "Unforced Error", "Forced Error"], key="result")

        detail = ""
        if result == "Ace":
            detail = st.radio("Ace Location", ["Wide", "Body", "T"], key="ace_detail")
        elif result in ["Winner", "Unforced Error", "Forced Error"]:
            detail = st.radio("Shot Type", ["Forehand", "Backhand"], key="shot_detail")

        if st.form_submit_button("✅ Save Point"):
            win_idx = st.session_state.players.index(winner)
            lose_idx = 1 - win_idx
            rally = st.session_state.rally_length

            st.session_state.stats[win_idx]["tpw"] += 1
            if rally <= 4:
                st.session_state.stats[win_idx]["rally_0_4"] += 1
            elif rally <= 8:
                st.session_state.stats[win_idx]["rally_5_8"] += 1
            else:
                st.session_state.stats[win_idx]["rally_9+"] += 1

            if result == "Ace":
                st.session_state.stats[win_idx]["aces"] += 1
            elif result == "Winner":
                st.session_state.stats[win_idx]["winners"] += 1
            elif result == "Unforced Error":
                st.session_state.stats[lose_idx]["ue"] += 1
            elif result == "Forced Error":
                st.session_state.stats[lose_idx]["fe"] += 1

            # Serve tracking
            if st.session_state.serve == "First":
                st.session_state.stats[server]["1st_serves"] += 1
                st.session_state.stats[server]["1st_won"] += int(win_idx == server)
                st.session_state.stats[lose_idx]["returns_1st"][1] += 1
                st.session_state.stats[lose_idx]["returns_1st"][0] += int(win_idx == lose_idx)
            else:
                st.session_state.stats[server]["2nd_serves"] += 1
                st.session_state.stats[server]["2nd_won"] += int(win_idx == server)
                st.session_state.stats[lose_idx]["returns_2nd"][1] += 1
                st.session_state.stats[lose_idx]["returns_2nd"][0] += int(win_idx == lose_idx)

            # Update game score
            st.session_state.points[win_idx] += 1
            if st.session_state.points[win_idx] >= 4 and st.session_state.points[win_idx] - st.session_state.points[lose_idx] >= 2:
                st.session_state.games[win_idx] += 1
                st.session_state.points = [0, 0]
                st.session_state.server = get_next_server(server, st.session_state.is_doubles)
                if st.session_state.games[win_idx] >= 6 and (st.session_state.games[win_idx] - st.session_state.games[lose_idx] >= 2):
                    st.session_state.sets[st.session_state.current_set][win_idx] += 1
                    st.session_state.current_set += 1 if st.session_state.current_set < 3 else 0
                    st.session_state.games = [0, 0]
            st.rerun()

    if st.button("🔚 End Match and Generate AI Feedback"):
        winner = get_set_winner(st.session_state.sets)
        summary = f"🏆 Winner: {st.session_state.players[winner]}\n\n"
        for i in range(2):
            stats = st.session_state.stats[i]
            summary += f"\n**{st.session_state.players[i]} Stats**\n"
            summary += f"- Aces: {stats['aces']}\n- Double Faults: {stats['dfs']}\n- Winners: {stats['winners']}\n- Unforced Errors: {stats['ue']}\n- Forced Errors: {stats['fe']}\n"
            summary += f"- 1st Serve %: {stats['1st_won']}/{stats['1st_serves']}\n"
            summary += f"- 2nd Serve %: {stats['2nd_won']}/{stats['2nd_serves']}\n"
            summary += f"- Return 1st %: {stats['returns_1st'][0]}/{stats['returns_1st'][1]}\n"
            summary += f"- Return 2nd %: {stats['returns_2nd'][0]}/{stats['returns_2nd'][1]}\n"
            summary += f"- Total Points Won: {stats['tpw']}\n"
            summary += f"- Rallies 0–4: {stats['rally_0_4']} | 5–8: {stats['rally_5_8']} | 9+: {stats['rally_9+']}\n"
        st.text_area("Match Summary and Feedback", summary, height=400)
