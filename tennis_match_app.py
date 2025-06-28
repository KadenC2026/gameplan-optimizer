# tennis_match_app.py (updated with set win and feedback fix)
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Tennis Match Tracker", layout="wide")

# Helper functions and session initialization remain the same (truncated here for brevity)
# ...

# Match UI (existing content above this remains unchanged)

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

            # Check for set win
            g1, g2 = st.session_state.games
            if g1 >= 6 and g1 - g2 >= 2:
                st.session_state.sets[st.session_state.current_set][0] += 1
                st.session_state.games = [0, 0]
                st.session_state.current_set += 1 if st.session_state.current_set < 3 else 0
            elif g2 >= 6 and g2 - g1 >= 2:
                st.session_state.sets[st.session_state.current_set][1] += 1
                st.session_state.games = [0, 0]
                st.session_state.current_set += 1 if st.session_state.current_set < 3 else 0

        st.rerun()

    if st.button("🔚 End Match and Generate AI Feedback"):
        winner = get_set_winner(st.session_state.sets)
        summary = f"🏆 Winner: {st.session_state.players[winner]}\n\n" if winner is not None else "Match not yet decided.\n\n"
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

        st.text_area("📊 Match Summary and Feedback", summary, height=400)
