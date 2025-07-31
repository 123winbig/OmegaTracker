import streamlit as st
import random
import pandas as pd

# ----- REALISTIC EUROPEAN WHEEL LAYOUT -----
wheel_layout = [0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 
                6, 27, 13, 36, 11, 30, 8, 23, 10, 5, 
                24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 
                29, 7, 28, 12, 35, 3, 26]

# ----- INITIAL STATE -----
if "history" not in st.session_state:
    st.session_state["history"] = []
if "balance" not in st.session_state:
    st.session_state["balance"] = 100

base_stake = 1
history = st.session_state["history"]
balance = st.session_state["balance"]

# ----- NEIGHBOR DETECTION -----
def get_neighbors(number):
    if number not in wheel_layout:
        return []
    index = wheel_layout.index(number)
    left = wheel_layout[(index - 1) % len(wheel_layout)]
    right = wheel_layout[(index + 1) % len(wheel_layout)]
    return [left, right]

# ----- HOT NUMBER DETECTION -----
def get_hot(spins, n=5):
    return pd.Series(spins).value_counts().head(n).index.tolist()

# ----- ECHO ZONE (Recent Repeats) -----
def get_echo_zone(spins, n=6):
    recent = spins[-n:]
    return [num for num in set(recent) if recent.count(num) > 1]

# ----- PREDICTION ENGINE -----
def get_predictions(spins):
    hot = get_hot(spins)
    echo = get_echo_zone(spins)
    neighbors = [nbr for spin in spins[-3:] for nbr in get_neighbors(spin)]

    counts = {}
    for num in hot:
        counts[num] = counts.get(num, 0) + 3
    for num in neighbors:
        counts[num] = counts.get(num, 0) + 2
    for num in echo:
        counts[num] = counts.get(num, 0) + 1

    return [{"number": num, "weight": wt} for num, wt in counts.items()]

# ----- STAKE SCALING -----
def recommend_stake(predictions):
    total_weight = sum(p["weight"] for p in predictions)
    max_weight = len(predictions) * 3
    confidence = total_weight / max_weight if max_weight else 0

    if confidence <= 0.3:
        stake = base_stake
    elif confidence <= 0.6:
        stake = base_stake * 2
    elif confidence <= 0.9:
        stake = base_stake * 3
    else:
        stake = base_stake * 5

    return round(confidence * 100, 1), stake

# ----- STREAMLIT INTERFACE -----
st.title("🎡 OmegaTracker v1.2")
st.subheader("European Wheel + Smart Prediction + Real-Time Strategy")

st.number_input("💰 Starting Balance", value=balance, step=1, key="balance")

if st.button("🎲 Spin Wheel"):
    spin = random.choice(wheel_layout)
    history.append(spin)
    st.session_state["history"] = history
    st.write(f"🎯 Spin Result: **{spin}**")

    if len(history) >= 12:
        predictions = get_predictions(history)
        confidence, stake = recommend_stake(predictions)

        st.metric("📊 Prediction Confidence", f"{confidence}%")
        st.metric("💵 Suggested Stake", f"€{stake}")

        pred_df = pd.DataFrame(predictions)
        st.dataframe(pred_df)

        st.line_chart(pd.Series([balance + (stake if spin in pred_df['number'].values else -stake)
                                 for spin in history]))
    else:
        st.info("🔍 Spin at least 12 times to activate predictions.")

# ----- SESSION EXPORT -----
if st.button("📁 Export Session"):
    df = pd.DataFrame({
        "Spin #": list(range(1, len(history) + 1)),
        "Result": history
    })
    st.download_button("📥 Download CSV", df.to_csv(index=False), "omega_session.csv", "text/csv")
