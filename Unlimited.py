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

STAKE_PROGRESSIONS = [1, 1, 2, 2, 3, 4, 5, 5, 8]

class OmegaTracker:
    def __init__(self, bankroll, unit_value):
        self.spin_history = []
        self.frequency = defaultdict(int)
        self.miss_count = {i: 0 for i in range(37)}
        self.bankroll = bankroll
        self.unit_value = unit_value
        self.predicted_last = None
        self.progress_step = 0

    def add_spin(self, number):
        if not 0 <= number <= 36:
            return f"❌ Invalid spin: {number}"
        self.spin_history.append(number)
        self.frequency[number] += 1
        for i in range(37):
            self.miss_count[i] += 1
        self.miss_count[number] = 0

        # Bankroll update on win
        if self.predicted_last and number == self.predicted_last:
            win_amt = self.unit_value * STAKE_PROGRESSIONS[self.progress_step] * 36
            self.bankroll += win_amt
            self.progress_step = 0
        elif self.progress_step < len(STAKE_PROGRESSIONS) - 1:
            self.progress_step += 1

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
        return sorted(
            {i: self.frequency[i] * 2 + self.miss_count[i] for i in range(37)}.items(),
            key=lambda x: x[1], reverse=True
        )

    def reason(self, pocket):
        f, m = self.frequency[pocket], self.miss_count[pocket]
        if f > 0 and m < 5: return "🔥 Hot & recently hit"
        if f == 0 and m > 20: return "❄️ Cold & overdue"
        if f > 1: return "📈 Active trend"
        return "🧠 Pattern match"

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

    def predict(self):
        if len(self.spin_history) < 12:
            return "⚠️ Need 12+ spins for prediction"
        best = self.score_pockets()[0][0]
        self.predicted_last = best
        group_id = self.kaprekar_seed()
        group = POCKET_GROUPS.get(group_id, [])
        if best in group:
            idx = group.index(best)
            display = f"[{group[idx - 1]}] <{best}> [{group[idx + 1]}]" if 0 < idx < len(group)-1 else str(group)
        else:
            display = str(group)
        backup = next((i for i in group if i != best), None)
        stake_units = STAKE_PROGRESSIONS[self.progress_step]
        stake_amount = self.unit_value * stake_units
        return {
            "Best Bet": best,
            "1NB Group": display,
            "Backup": backup,
            "Reason Best": self.reason(best),
            "Reason Backup": self.reason(backup),
            "Avg Jump": self.average_jump(),
            "Stake Advice": f"💸 Step {self.progress_step+1}/9: Stake €{stake_amount:.2f}"
        }

    def top_hot(self): return sorted(self.frequency.items(), key=lambda x: x[1], reverse=True)[:5]
    def top_cold(self): return sorted(self.miss_count.items(), key=lambda x: x[1], reverse=True)[:5]

# Streamlit UI
st.set_page_config("OmegaTracker v2.3", "🎰")
st.title("🎰 OmegaTracker v2.3 — Precision Roulette Companion")

bankroll = st.number_input("💰 Starting Bankroll (€)", min_value=10.0, step=10.0)
unit_value = st.number_input("🔢 Base Stake Unit (€)", min_value=1.0, step=1.0)
tracker = OmegaTracker(bankroll, unit_value)

spin_input = st.text_input("🎲 Enter spin results (comma or space-separated):")
if spin_input:
    try:
        cleaned = spin_input.replace(",", " ").split()
        spins = [int(s.strip()) for s in cleaned]
        for s in spins:
            msg = tracker.add_spin(s)
            if msg:
                st.warning(msg)
    except:
        st.error("❌ Invalid format — enter numbers 0–36 using commas or spaces.")

if len(tracker.spin_history) >= 12:
    st.subheader("🔮 Tactical Prediction")
    prediction = tracker.predict()
    if isinstance(prediction, str):
        st.info(prediction)
    else:
        st.success(f"🎯 Best Bet: {prediction['Best Bet']} — {prediction['Reason Best']}")
        st.info(f"⚡ 1NB Backup: {prediction['Backup']} — {prediction['Reason Backup']}")
        st.write(f"🧠 Group Display: {prediction['1NB Group']}")
        st.write(f"🔁 Avg Wheel Jump: {prediction['Avg Jump']}")
        st.write(f"{prediction['Stake Advice']}")
        st.write(f"📈 Updated Bankroll: €{round(tracker.bankroll, 2)}")

if tracker.spin_history:
    st.subheader("📊 Pocket Activity")
    hot = tracker.top_hot()
    cold = tracker.top_cold()
    st.write("🔥 Hot Pockets:", {num: f"{freq}x" for num, freq in hot})
    st.write("❄️ Cold P
