# omega_tracker_v2.py

import streamlit as st
from collections import defaultdict

# European roulette wheel sequence (physical layout)
WHEEL_ORDER = [
    0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36,
    11, 30, 8, 23, 10, 5, 24, 16, 33, 1, 20, 14, 31, 9,
    22, 18, 29, 7, 28, 12, 35, 3, 26
]

class OmegaTracker:
    def __init__(self, bankroll):
        self.spin_history = []
        self.bankroll = bankroll
        self.frequency = defaultdict(int)
        self.miss_count = {i: 0 for i in range(37)}

    def add_spin(self, number):
        if not 0 <= number <= 36:
            return f"❌ Invalid input: {number}. Only numbers 0–36 allowed."
        self.spin_history.append(number)
        self.frequency[number] += 1
        for i in range(37):
            self.miss_count[i] += 1
        self.miss_count[number] = 0

    def physical_jump_distance(self):
        if len(self.spin_history) < 2:
            return 0
        jumps = []
        for i in range(1, len(self.spin_history)):
            prev = self.spin_history[i - 1]
            curr = self.spin_history[i]
            try:
                index_prev = WHEEL_ORDER.index(prev)
                index_curr = WHEEL_ORDER.index(curr)
                jump = abs(index_curr - index_prev)
                jumps.append(jump)
            except ValueError:
                continue
        return round(sum(jumps) / len(jumps), 2) if jumps else 0

    def score_pockets(self):
        scores = {}
        for i in range(37):
            freq = self.frequency[i]
            miss = self.miss_count[i]
            scores[i] = freq * 2 + miss
        return sorted(scores.items(), key=lambda x: x[1], reverse=True)

    def predict(self):
        if len(self.spin_history) < 12:
            return "⚠️ Not enough spins. Enter at least 12 to unlock predictions."
        ranked = self.score_pockets()
        best, backup = ranked[0], ranked[1]
        avg_jump = self.physical_jump_distance()
        return {
            "Best Bet": best[0],
            "1NB Backup": backup[0],
            "Reason Best": f"Hit {self.frequency[best[0]]}x, missed {self.miss_count[best[0]]} spins",
            "Reason 1NB": f"Hit {self.frequency[backup[0]]}x, missed {self.miss_count[backup[0]]} spins",
            "Avg Jump Distance": avg_jump,
            "Stake Advice": self.stake_advice(best[1])
        }

    def stake_advice(self, score):
        if score > 25:
            return f"🔥 High confidence — bet up to {self.bankroll * 0.2:.2f}"
        elif score > 15:
            return f"⚡ Medium confidence — bet up to {self.bankroll * 0.1:.2f}"
        else:
            return f"🧊 Low confidence — bet max {self.bankroll * 0.05:.2f}"

# 🎯 Streamlit Interface
st.set_page_config(page_title="OmegaTracker v2.0", page_icon="🎰")
st.title("🎲 OmegaTracker v2.0 – Intelligent Roulette Assistant")

# Bankroll input
bankroll = st.number_input("💰 Enter your bankroll (€):", min_value=10, step=10)
tracker = OmegaTracker(bankroll)

# Spin input field
spin_input = st.text_input("🎯 Enter spin results (comma-separated, e.g., 5,16,23):")

# Process spin entries
if spin_input:
    try:
        numbers = [int(num.strip()) for num in spin_input.split(",")]
        for num in numbers:
            result = tracker.add_spin(num)
            if result:
                st.warning(result)
    except Exception:
        st.error("❌ Please enter valid numbers separated by commas.")

# Show statistics
if tracker.spin_history:
    st.subheader("📊 Pocket Statistics")
    st.write(f"Total Spins: {len(tracker.spin_history)}")
    st.write(f"Average Physical Jump Distance: {tracker.physical_jump_distance()}")

    with st.expander("🔍 Frequency & Miss Count"):
        freq = {i: tracker.frequency[i] for i in range(37) if tracker.frequency[i] > 0}
        miss = {i: tracker.miss_count[i] for i in range(37)}
        st.write("🟢 Frequency:", freq)
        st.write("🔴 Miss Count:", miss)

    # Show predictions
    st.subheader("🔮 Predictions")
    prediction = tracker.predict()
    if isinstance(prediction, str):
        st.info(prediction)
    else:
        st.success(f"Best Bet: 🎯 {prediction['Best Bet']}")
        st.write(f"1NB Backup: ⚡ {prediction['1NB Backup']}")
        st.write(f"Reason: {prediction['Reason Best']}")
        st.write(f"1NB Reason: {prediction['Reason 1NB']}")
        st.write(f"Avg Jump Distance: 🔁 {prediction['Avg Jump Distance']}")
        st.write(f"Stake Advice: 💰 {prediction['Stake Advice']}")
