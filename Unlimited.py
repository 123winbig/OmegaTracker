import streamlit as st
from collections import defaultdict

WHEEL_ORDER = [
    0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6,
    27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16,
    33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28,
    12, 35, 3, 26
]

class OmegaTracker:
    def __init__(self):
        self.spin_history = []
        self.progression = [1, 2, 3, 4]  # stakes per pocket
        self.current_step = 0
        self.bankroll = 0
        self.total_bet_units = 0

    def get_neighbors(self, number):
        idx = WHEEL_ORDER.index(number)
        left = WHEEL_ORDER[(idx - 1) % len(WHEEL_ORDER)]
        right = WHEEL_ORDER[(idx + 1) % len(WHEEL_ORDER)]
        return left, right

    def best_bet(self):
        return WHEEL_ORDER[len(self.spin_history) % len(WHEEL_ORDER)]

    def backup_bet(self):
        if len(self.spin_history) >= 2:
            src = self.spin_history[-2]
        else:
            src = WHEEL_ORDER[7]
        return src

    def get_bet_spread(self, center):
        left, right = self.get_neighbors(center)
        return [left, center, right]

    def add_spin(self, result):
        self.spin_history.append(result)
        stake = self.progression[self.current_step]
        primary = self.get_bet_spread(self.best_bet())
        backup = self.get_bet_spread(self.backup_bet())
        all_pockets = primary + backup
        total_bet = stake * 6
        self.total_bet_units += total_bet

        # Hit detection
        hits = []
        if result in primary:
            hits.append('Primary')
        if result in backup and result not in primary:
            hits.append('Backup')

        payout = len(hits) * stake * 36
        net_result = payout - total_bet
        self.bankroll += net_result

        # Progression reset if any hit
        if hits:
            self.current_step = 0
            print(f"✅ HIT in {' & '.join(hits)} → +€{payout} | Net: €{net_result}")
        else:
            self.current_step = min(self.current_step + 1, len(self.progression) - 1)
            print(f"❌ Miss → Loss: €{total_bet} | Progression → Step {self.current_step}")

        print(f"💰 Bankroll: €{self.bankroll} | Total Units Bet: {self.total_bet_units}\n")

    def show_next_bet(self):
        stake = self.progression[self.current_step]
        primary = self.get_bet_spread(self.best_bet())
        backup = self.get_bet_spread(self.backup_bet())
        print(f"🎯 Next Bets:")
        print(f"🔹 Primary Spread → {primary}")
        print(f"🔸 Backup Spread → {backup}")
        print(f"🧾 Stake: €{stake} × 6 pockets → €{stake * 6}\n")

# 🔥 Demo
tracker = OmegaTracker()
tracker.show_next_bet()
tracker.add_spin(28)
tracker.show_next_bet()
tracker.add_spin(2)
tracker.show_next_bet()
