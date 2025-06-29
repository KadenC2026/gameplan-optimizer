import streamlit as st
import json
import openai
from datetime import datetime

# 🔐 Set your API key
openai.api_key = "Fakekey"

st.set_page_config(page_title="Tennis Match Tracker", layout="wide")

# --- Session state setup ---
if 'step' not in st.session_state:
    st.session_state.step = 'start'
    st.session_state.match_info = {
        'format': '',
        'players': ['', '', '', ''],
        'surface': '', 'speed': '', 'type': '',
        'temp': '', 'humidity': '', 'conditions': '',
        'server': 0
    }
    st.session_state.score = {'sets': [0, 0], 'games': [0, 0], 'points': [0, 0]}
    st.session_state.stats = {
        'players': [
            { 'aces': 0, 'doubleFaults': 0, 'winners': 0, 'forcedErrors': 0, 'unforcedErrors': 0,
              'totalPoints': 0, 'pointsWon': 0, 'rallyCounts': {'0-4': 0, '5-8': 0, '9+': 0}, 'netApproaches': 0 },
            { 'aces': 0, 'doubleFaults': 0, 'winners': 0, 'forcedErrors': 0, 'unforcedErrors': 0,
              'totalPoints': 0, 'pointsWon': 0, 'rallyCounts': {'0-4': 0, '5-8': 0, '9+': 0}, 'netApproaches': 0 }
        ]
    }
    st.session_state.ai_feedback = ''

# --- Functions ---
def generate_feedback(stats):
    prompt = f"""A tennis player just completed a match. Here are their stats:
{json.dumps(stats, indent=2)}

Give feedback on strengths, weaknesses, and what they can improve next time."""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message['content']

# --- UI Logic ---
if st.session_state.step == 'start':
    st.title("🎾 Tennis Match Tracker")
    if st.button("Start a Match"):
        st.session_state.step = 'format'

elif st.session_state.step == 'format':
    st.header("Choose Match Format")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Singles"):
            st.session_state.match_info['format'] = 'singles'
            st.session_state.step = 'enterPlayers'
    with col2:
        if st.button("Doubles"):
            st.session_state.match_info['format'] = 'doubles'
            st.session_state.step = 'enterPlayers'

elif st.session_state.step == 'enterPlayers':
    st.header("Enter Player and Court Info")
    n = 2 if st.session_state.match_info['format'] == 'singles' else 4
    for i in range(n):
        st.session_state.match_info['players'][i] = st.text_input(f"Player {i+1}", key=f"p{i}")

    st.session_state.match_info['surface'] = st.selectbox("Court Surface", ['hard', 'clay', 'grass'])
    st.session_state.match_info['speed'] = st.selectbox("Court Speed", ['slow', 'neutral', 'fast'])
    st.session_state.match_info['type'] = st.selectbox("Court Type", ['indoor', 'outdoor'])
    st.session_state.match_info['temp'] = st.text_input("Temperature (°C)")
    st.session_state.match_info['humidity'] = st.text_input("Humidity (%)")
    st.session_state.match_info['conditions'] = st.text_input("Other Conditions")

    if st.button("Start Match"):
        st.session_state.step = 'match'

elif st.session_state.step == 'match':
    st.header(f"Match in Progress - {datetime.today().strftime('%Y-%m-%d')}")
    st.subheader("Scores")
    cols = st.columns(2)
    for i in [0, 1]:
        with cols[i]:
            st.write(f"{st.session_state.match_info['players'][i] or f'Player {i+1}'}")
            st.write(f"Sets: {st.session_state.score['sets'][i]} | Games: {st.session_state.score['games'][i]} | Points: {st.session_state.score['points'][i]}")
            if st.button(f"+ Point for Player {i+1}", key=f"pt{i}"):
                st.session_state.stats['players'][i]['pointsWon'] += 1
                st.session_state.stats['players'][i]['totalPoints'] += 1
                st.session_state.step = 'logPoint'

    st.write("""---""")
    if st.button("End Match and Generate Feedback"):
        st.session_state.ai_feedback = generate_feedback(st.session_state.stats)
        st.session_state.step = 'feedback'

elif st.session_state.step == 'logPoint':
    st.subheader("Log Point Outcome")
    st.radio("Point Outcome", ['Ace', 'Winner', 'Unforced Error', 'Forced Error'], key='outcome')
    st.slider("Rally Length", 0, 100, 5, key='rally')
    st.checkbox("Player 1 Came to Net", key='net1')
    st.checkbox("Player 2 Came to Net", key='net2')
    if st.button("Save Point"):
        st.session_state.step = 'match'
    if st.button("Cancel"):
        st.session_state.step = 'match'

elif st.session_state.step == 'feedback':
    st.title("🧠 AI Match Feedback")
    st.markdown(st.session_state.ai_feedback)
    if st.button("Start Over"):
        for key in st.session_state.keys():
            del st.session_state[key]
