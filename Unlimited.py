# omega_tracker_v2_1.py

import streamlit as st
from collections import defaultdict

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
            return f"❌ Invalid number: {number} — must be between 0 and 36."
        self.spin_history.append(number)
        self.frequency[number] += 1
        for i in range(37):
            self.miss_count[i] += 1
        self.miss_count[number] = 0

    def average_jump(self):
        if len(self.spin_history) < 2:
            return 0
        jumps = []
        for i in range(1, len(self.spin_history)):
            try:
                prev = WHEEL_ORDER.index(self.spin_history[i-1])
                curr = WHEEL_ORDER.index(self.spin_history[i])
                jumps.append(abs(curr - prev))
            except ValueError:
                continue
        return round(sum(jumps) / len(jumps), 2) if jumps else 0

    def score_pockets(self):
        scores = {}
        for i in range(37):
            scores[i] = self.frequency[i] * 2 + self.miss_count[i]
        return sorted(scores.items(), key=lambda x: x[1], reverse=True)

    def reason(self, pocket):
        freq = self.frequency[pocket]
        miss = self.miss_count[pocket]
        if freq > 0 and miss < 5:
            return "🔥 Hot pocket recently hit"
        elif freq == 0 and miss > 20:
            return "💤 Cold pocket highly overdue"
        elif freq > 1:
            return "📈 Trending with frequent hits"
        else:
            return "🧠 Strategically selected by pattern score"

    def predict(self):
        if len(self.spin_history) < 12:
            return "⚠️ Need at least 12 spins for prediction."
        ranked = self.score_pockets()
        best, backup = ranked[0][0], ranked[1][0]
        return {
            "Best Bet": best,
            "1NB Backup": backup,
            "Best Reason": self.reason(best),
            "1NB Reason": self.reason(backup),
            "Avg Jump": self.average_jump(),
            "Stake Advice": self.stake(best)
        }

    def stake(self, score_key):
        score = self.frequency[score_key]*2 + self.miss_count[score_key]
        if score > 25:
            return f"✅ High confidence — stake up to €{self.bankroll*0.2:.2f}"
        elif score > 15:
            return f"⚖️ Moderate confidence — stake up to €{self.bankroll*0.1:.2f}"
        else:
            return f"⚠️ Low confidence — stake max €{self.bankroll*0.05:.2f}"

    def top_hot(self):
        return sorted(self.frequency.items(), key=lambda x: x[1], reverse=True)[:5]

    def top_cold(self):
        return sorted(self.miss_count.items(), key=lambda x: x[1], reverse=True)[:5]

# 🖥️ Streamlit interface
st.set_page_config("OmegaTracker v2.1", "🎰")
st.title("🎯 OmegaTracker v2.1 – Pocket-Aware Roulette Intelligence")

bankroll = st.number_input("💰 Enter your starting bankroll:", min_value=10, step=10)
tracker = OmegaTracker(bankroll)

spin_input = st.text_input("🎲 Enter spin results (comma-separated):")
if spin_input:
    try:
        spins = [int(s.strip()) for s in spin_input.split(",")]
        for s in spins:
            msg = tracker.add_spin(s)
            if msg:
                st.warning(msg)
    except:
        st.error("Invalid input — please use comma-separated numbers only.")

# 🔮 Predictions FIRST
if tracker.spin_history and len(tracker.spin_history) >= 12:
    st.subheader("🔮 Tactical Prediction")
    prediction = tracker.predict()
    if isinstance(prediction, str):
        st.info(prediction)
    else:
        st.success(f"🎯 Best Bet: {prediction['Best Bet']} — {prediction['Best Reason']}")
        st.info(f"⚡ 1NB Backup: {prediction['1NB Backup']} — {prediction['1NB Reason']}")
        st.write(f"🔁 Avg Wheel Jump: {prediction['Avg Jump']}")
        st.write(f"💰 {prediction['Stake Advice']}")

        # Optional hit confirmation
        hit_confirm = st.checkbox("✅ Did your Best Bet hit?")
        if hit_confirm:
            st.success("🎉 Bankroll win recorded!")
            win_amt = bankroll * 0.2
            st.write(f"🆙 New Balance: €{bankroll + win_amt:.2f}")

# 📊 Slimmed Statistics
if tracker.spin_history:
    st.subheader("📊 Top Pocket Stats")
    hot = tracker.top_hot()
    cold = tracker.top_cold()

    st.write("🔥 Top 5 Hot Pockets:")
    st.write({num: f"{freq}x" for num, freq in hot})

    st.write("❄️ Top 5 Cold Pockets:")
    st.write({num: f"Missed {miss} spins" for num, miss in cold})
