import streamlit as st
from collections import Counter, defaultdict

# 🧠 Init session state
if 'history' not in st.session_state:
    st.session_state['history'] = []
if 'bets' not in st.session_state:
    st.session_state['bets'] = []

# 🎰 App Title
st.title("🎯 OmegaTracker v1.4: Rule the Wheel")

# 🔄 Spin Entry
st.subheader("📥 Enter Spin Outcome")
new_spin = st.text_input("Latest Spin (number or color)", key="spin_input")

if st.button("Add Spin") and new_spin:
    st.session_state['history'].append(new_spin)
    st.success(f"Spin '{new_spin}' added!")

st.write(f"🧮 Spins Entered: {len(st.session_state['history'])}")
st.write("📜 History:", st.session_state['history'])

# ⏳ Gate: wait for 12 spins
if len(st.session_state['history']) < 12:
    st.warning("⏳ Enter at least 12 spins to activate predictions and tracking.")
    st.stop()

# 🧮 Frequency Analysis
def get_predictions(history):
    freq = Counter(history)
    most_common = freq.most_common(3)
    prediction = most_common[0][0]
    confidence = freq[prediction] / len(history)
    return prediction, confidence, freq

# 📉 Miss Count Tracker
def get_miss_counts(history):
    last_seen = {}
    for idx, val in enumerate(reversed(history)):
        if val not in last_seen:
            last_seen[val] = idx + 1
    return last_seen

# 💸 Stake Suggestion Engine
def suggest_stake(confidence, base=1.0):
    if confidence > 0.4:
        return round(base * 2, 2)
    elif confidence > 0.3:
        return round(base * 1.5, 2)
    else:
        return round(base, 2)

# 🔮 Prediction + UI Display
prediction, confidence, freq = get_predictions(st.session_state['history'])
stake = suggest_stake(confidence)
miss = get_miss_counts(st.session_state['history'])

st.subheader("🔮 Prediction Engine")
st.success(f"Bet Recommendation: **{prediction}**")
st.info(f"Confidence Score: {confidence:.2f}")
st.info(f"Suggested Stake: 💰 {stake} units")

# 🗺️ Wheel Layout Heatmap (simple placeholder)
st.subheader("🗺️ Wheel Layout")
st.write(freq)

# 📉 Miss Counts
st.subheader("📉 Missed Outcomes")
st.write(miss)

# ➕ Log Bet
if st.button("Log Bet"):
    st.session_state['bets'].append({
        "bet": prediction,
        "stake": stake,
        "confidence": confidence
    })
    st.success("Bet logged!")

# 🧾 Bet History
st.subheader("🔁 Bet History")
st.write(st.session_state['bets'])
