import streamlit as st
from collections import defaultdict

# Real European wheel layout
WHEEL_ORDER = [
    0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36,
    11, 30, 8, 23, 10, 5, 24, 16, 33, 1, 20, 14, 31, 9,
    22, 18, 29, 7, 28, 12, 35, 3, 26
]

# Pocket behavior clusters (12 groups)
POCKET_GROUPS = {
    1: [0, 32, 15],  2: [19, 4, 21],  3: [2, 25, 17],
    4: [34, 6, 27],  5: [13, 36, 11], 6: [30, 8, 23],
    7: [10, 5, 24],  8: [16, 33, 1],  9: [20, 14, 31],
    10: [9, 22, 18], 11: [29, 7, 28], 12: [12, 35, 3, 26]
}

class OmegaTracker:
    def __init__(self, bankroll):
        self.spin_history = []
        self.frequency = defaultdict(int)
        self.miss_count = {i: 0 for i in range(37)}
        self.bankroll = bankroll
        self.predicted_last = None

    def add_spin(self, number):
        if not 0 <= number <= 36:
            return f"❌ Invalid spin: {number} — only 0–36 allowed."
        self.spin_history.append(number)
        self.frequency[number] += 1
        for i in range(37):
            self.miss_count[i] += 1
        self.miss_count[number] = 0

        # Auto bankroll update if predicted hit
        if self.predicted_last and number == self.predicted_last:
            win_amt = self.bankroll * 0.2
            self.bankroll += win_amt

    def average_jump(self):
        if len(self.spin_history) < 2:
            return 0
        jumps = []
        for i in range(1, len(self.spin_history)):
            try:
                idx1 = WHEEL_ORDER.index(self.spin_history[i - 1])
                idx2 = WHEEL_ORDER.index(self.spin_history[i])
                jumps.append(abs(idx2 - idx1))
            except ValueError:
                continue
        return round(sum(jumps) / len(jumps), 2) if jumps else 0

    def kaprekar_seed(self):
        if len(self.spin_history) < 4:
            return None
        digits = self.spin_history[-4:]
        num = int("".join([str(d).zfill(2) for d in digits])) % 10000
        for _ in range(7):
            asc = int("".join(sorted(str(num).zfill(4))))
            desc = int("".join(sorted(str(num).zfill(4), reverse=True)))
            num = desc - asc
            if num == 6174:
                break
        return num % 12 + 1

    def score_pockets(self):
        scores = {}
        for i in range(37):
            scores[i] = self.frequency[i] * 2 + self.miss_count[i]
        return sorted(scores.items(), key=lambda x: x[1], reverse=True)

    def reason(self, pocket):
        f = self.frequency[pocket]
        m = self.miss_count[pocket]
        if f > 0 and m < 5: return "🔥 Hot and recently hit"
        if f == 0 and m > 20: return "❄️ Very cold and overdue"
        if f > 1: return "📈 Consistently active"
        return "🧠 Strategic pattern match"

    def predict(self):
        if len(self.spin_history) < 12:
            return "⚠️ Need 12+ spins for prediction"
        ranked = self.score_pockets()
        best = ranked[0][0]
        self.predicted_last = best  # store for win check
        group = self.kaprekar_seed()
        backup = next((i for i in POCKET_GROUPS[group] if i != best), None) if group else None
        return {
            "Best Bet": best,
            "1NB Backup": backup,
            "Reason Best": self.reason(best),
            "Reason 1NB": self.reason(backup) if backup is not None else "Derived from spin seed logic",
            "Avg Jump": self.average_jump(),
            "Stake Advice": self.stake(best)
        }

    def stake(self, key):
        score = self.frequency[key] * 2 + self.miss_count[key]
        if score > 25: return f"💰 High confidence – stake up to €{self.bankroll * 0.2:.2f}"
        if score > 15: return f"⚖️ Medium confidence – stake up to €{self.bankroll * 0.1:.2f}"
        return f"⚠️ Low confidence – stake max €{self.bankroll * 0.05:.2f}"

    def top_hot(self): return sorted(self.frequency.items(), key=lambda x: x[1], reverse=True)[:5]
    def top_cold(self): return sorted(self.miss_count.items(), key=lambda x: x[1], reverse=True)[:5]

# 🔷 Streamlit Interface
st.set_page_config("OmegaTracker v2.2", "🎰")
st.title("🎰 OmegaTracker v2.2 — Strategic Roulette Tracker")

bankroll = st.number_input("💰 Enter your starting bankroll", min_value=10, step=10)
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
        st.error("Invalid format — enter numbers between 0–36, separated by commas.")

# 🔮 Predictions
if len(tracker.spin_history) >= 12:
    st.subheader("🧠 Tactical Prediction")
    prediction = tracker.predict()
    if isinstance(prediction, str):
        st.info(prediction)
    else:
        st.success(f"🎯 Best Bet: {prediction['Best Bet']} — {prediction['Reason Best']}")
        st.info(f"⚡ 1NB Backup: {prediction['1NB Backup']} — {prediction['Reason 1NB']}")
        st.write(f"🔁 Avg Wheel Jump Distance: {prediction['Avg Jump']}")
        st.write(f"💰 {prediction['Stake Advice']}")
        st.write(f"📈 Updated Bankroll: €{round(tracker.bankroll, 2)}")

# 📊 Key Stats
if tracker.spin_history:
    st.subheader("📊 Pocket Activity")
    hot = tracker.top_hot()
    cold = tracker.top_cold()
    st.write("🔥 Top 5 Hot Pockets:", {num: f"{freq}x" for num, freq in hot})
    st.write("❄️ Top 5 Cold Pockets:", {num: f"Missed {miss} spins" for num, miss in cold})
