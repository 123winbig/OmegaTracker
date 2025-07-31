import streamlit as st
from collections import Counter

# 🎲 Roulette Column Mapping
def get_column(number):
    col1 = {1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34}
    col2 = {2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35}
    col3 = {3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36}
    try:
        n = int(number)
    except:
        return None
    if n in col1:
        return 1
    elif n in col2:
        return 2
    elif n in col3:
        return 3
    return None

# ⚙️ Setup State
if 'history' not in st.session_state:
    st.session_state['history'] = []
if 'miss_tracker' not in st.session_state:
    st.session_state['miss_tracker'] = {}

# 🎰 UI Title
st.title("🎯 OmegaTracker v1.6 - Column-Aware Tactical Betting")

# ➕ Spin Entry
new_spin = st.text_input("Enter Spin Outcome (1–36)")
if st.button("Submit Spin") and new_spin:
    st.session_state['history'].append(new_spin)

    # 🧠 Update Miss Tracker
    for outcome in st.session_state['miss_tracker']:
        st.session_state['miss_tracker'][outcome] += 1
    if new_spin not in st.session_state['miss_tracker']:
        st.session_state['miss_tracker'][new_spin] = 0
    else:
        st.session_state['miss_tracker'][new_spin] = 0

    st.success(f"Spin '{new_spin}' logged.")

# ⏳ Hold Until 12 Spins
total_spins = len(st.session_state['history'])
if total_spins < 12:
    st.warning("⏳ Prediction engine activates after 12 spins.")
    st.stop()

# 🔄 Column Progression Analysis
column_sequence = [get_column(s) for s in st.session_state['history'] if get_column(s) is not None]
column_moves = []
for i in range(1, len(column_sequence)):
    move = column_sequence[i] - column_sequence[i-1]
    column_moves.append(move)

avg_move = round(sum(column_moves) / len(column_moves), 2) if column_moves else 0

# 🎯 Prediction Logic
freq = Counter(st.session_state['history'])
predicted = freq.most_common(1)[0][0]
conf_score = freq[predicted] / total_spins
miss_count = st.session_state['miss_tracker'].get(predicted, 0)

# 💰 Stake Suggestion
def suggest_stake(confidence, base=1.0):
    if confidence > 0.4:
        return round(base * 2, 2)
    elif confidence > 0.3:
        return round(base * 1.5, 2)
    else:
        return round(base, 2)

stake = suggest_stake(conf_score)

# 📊 Tactical Output
st.subheader("🧠 Tactical Prediction")
st.metric(label="Predicted Outcome", value=predicted)
st.metric(label="Missed Count", value=f"{miss_count} spins")
st.metric(label="Suggested Stake", value=f"{stake} units")

# 🧠 Display Column Intelligence
st.subheader("📐 Column Strategy Engine")
st.metric(label="Avg Column Movement", value=f"{avg_move}")
st.write(f"Column Sequence: {column_sequence}")
st.write(f"Column Transitions: {column_moves}")

# 🧪 Auto-Switch Logic (coming soon!)
# At 24 or 36 spins, we could shift weighting from frequency to column patterning. Placeholder for now.
