import streamlit as st
from collections import Counter

class OmegaSystemUnlimited:
    def __init__(self, bankroll):
        self.original_bankroll = bankroll
        self.unit_bank = bankroll
        self.spins = []
        self.session_max = 108
        self.bet_progression = [1, 1, 1, 2, 2, 3, 4, 5, 9]
        self.bet_stage = 0
        self.kaprekar_groups = self.generate_kaprekar_groups()
        self.last_result = None
        self.last_prediction = []

    def reset_session(self):
        self.spins = []
        self.bet_stage = 0
        self.unit_bank = self.original_bankroll
        self.last_result = None
        self.last_prediction = []

    def add_spin(self, number):
        self.spins.append(number)
        if len(self.spins) >= self.session_max:
            self.reset_session()
        self.auto_bet()

    def get_hot_pockets(self):
        if len(self.spins) < 13:
            return []
        data = self.spins[12:105]
        counts = Counter(data)
        return [num for num, _ in counts.most_common(5)]

    def kaprekar_step(self, num_str):
        asc = ''.join(sorted(num_str))
        desc = ''.join(sorted(num_str, reverse=True))
        return str(int(desc) - int(asc)).zfill(4)

    def is_kaprekar_valid(self, num_str):
        return num_str not in ['1111', '2222', '3333', '4444', '5555', '6666', '7777', '8888', '9999']

    def get_kaprekar_seed(self, num_str):
        steps = 0
        seen = set()
        while num_str != '6174' and steps < 6:
            num_str = self.kaprekar_step(num_str)
            if num_str in seen or not self.is_kaprekar_valid(num_str):
                return None
            seen.add(num_str)
            steps += 1
        return num_str if num_str == '6174' else None

    def generate_kaprekar_groups(self):
        return {
            i: list(range(1 + (i - 1) * 4, 1 + i * 4)) for i in range(1, 10)
        }

    def get_kaprekar_prediction(self):
        seeds = []
        for spin in self.spins[:12]:
            seed = self.get_kaprekar_seed(str(spin).zfill(4))
            if seed:
                seeds.append(seed)

        group_hits = Counter()
        for i in range(1, int(min(len(self.spins), 105)/12)+1):
            spins_slice = self.spins[(i - 1) * 12: i * 12]
            for group_id, group_nums in self.kaprekar_groups.items():
                group_hits[group_id] += sum(1 for n in spins_slice if n in group_nums)

        top_groups = [gid for gid, _ in group_hits.most_common(3)]
        return [num for gid in top_groups for num in self.kaprekar_groups[gid]]

    def final_prediction(self):
        hot = self.get_hot_pockets()
        kaprekar = self.get_kaprekar_prediction()
        overlap = list(set(hot) & set(kaprekar))
        if overlap:
            return overlap
        return hot[:3] + kaprekar[:2]

    def auto_bet(self):
        chosen_numbers = self.final_prediction()
        self.last_prediction = chosen_numbers
        units_this_bet = len(chosen_numbers) * self.bet_progression[self.bet_stage]
        self.unit_bank -= units_this_bet

        last_spin = self.spins[-1] if self.spins else None
        self.last_result = "LOSS"
        if last_spin in chosen_numbers:
            winnings = 36 * self.bet_progression[self.bet_stage]
            self.unit_bank += winnings
            self.bet_stage = 0
            self.last_result = "WIN"
        else:
            self.bet_stage = min(self.bet_stage + 1, len(self.bet_progression) - 1)

    def get_dashboard(self):
        return {
            "Bank Units": self.unit_bank,
            "Current Bet Stage": self.bet_progression[self.bet_stage],
            "Hot Pocket Prediction": self.get_hot_pockets(),
            "Kaprekar Prediction": self.get_kaprekar_prediction(),
            "Final Prediction Used": self.last_prediction,
            "Last Spin Result": self.spins[-1] if self.spins else None,
            "Outcome": self.last_result,
            "Spin Count": len(self.spins)
        }

# STREAMLIT UI
st.title("🎰 Omega System UNLIMITED - Autopilot Edition")

if "system" not in st.session_state:
    bankroll = st.number_input("Enter your bankroll (units):", min_value=1, step=1)
    if bankroll:
        st.session_state.system = OmegaSystemUnlimited(bankroll)

system = st.session_state.get("system")

spin_input = st.number_input("Enter spin result:", min_value=0, max_value=36, step=1)
if st.button("Add Spin"):
    system.add_spin(spin_input)
    st.success("Spin processed and bet placed automatically.")

dashboard = system.get_dashboard()
st.subheader("📊 Dashboard")
for k, v in dashboard.items():
    st.write(f"{k}: {v}")

if st.button("Reset Session"):
    system.reset_session()
    st.success("Session reset!")
