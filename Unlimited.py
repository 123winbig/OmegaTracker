import streamlit as st
from collections import Counter

# ⚙️ Setup
if 'history' not in st.session_state:
    st.session_state['history'] = []
if 'miss_tracker' not in st.session_state:
    st.session_state['miss_tracker'] = {}

# 🎰 UI Title
st.title("🎯 OmegaTracker v1.5 - Tactical Betting Mode")

# ➕ Enter Spin
new_spin = st.text_input("Enter Spin Outcome")
if st.button("Submit Spin") and new_spin:
    st.session_state['history'].append(new_spin)
    
    # 🧠 Update miss tracker
    for outcome in st.session_state['miss_tracker']:
        st.session_state['miss_tracker'][outcome] += 1
    if new_spin not in st.session_state['miss_tracker']:
        st.session_state['miss_tracker'][new_spin] = 0
    else:
        st.session_state['miss_tracker'][new_spin] = 0
    st.success("Spin added.")

# ⏳ Wait for 12 spins
if len(st.session_state['history']) < 12:
    st.warning("⏳ Enter 12+ spins to activate prediction engine.")
    st.stop()

# 🔮 Prediction Engine
freq = Counter(st.session_state['history'])
predicted = freq.most_common(1)[0][0]
conf_score = freq[predicted] / len(st.session_state['history'])
miss_count = st.session_state['miss_tracker'].get(predicted, 0)

def suggest_stake(confidence, base=1.0):
    if confidence > 0.4:
        return round(base * 2, 2)
    elif confidence > 0.3:
        return round(base * 1.5, 2)
    else:
        return round(base, 2)

stake = suggest_stake(conf_score)

# 📊 Tactical Output
st.subheader("🎯 Tactical Prediction")
st.metric(label="Predicted Outcome", value=predicted)
st.metric(label="Missed Count", value=f"{miss_count} spins")
st.metric(label="Suggested Stake", value=f"💰 {stake} units")
