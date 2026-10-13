from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Optional, Tuple, Union, Any

class SusuGroup:
    def __init__(self, weekly_contribution: Union[str, float, Decimal]):
        self.weekly_contribution = Decimal(str(weekly_contribution)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        if self.weekly_contribution <= 0:
            raise ValueError("Weekly contribution must be greater than zero.")
        
        self.members: List[str] = []
        self.payout_history: List[Dict[str, Any]] = []
        # Structure: {week_number: {member_id: paid_amount_decimal}}
        self.contributions: Dict[int, Dict[str, Decimal]] = {1: {}}
        self.current_week: int = 1
        self.is_started: bool = False

    def add_member(self, member_id: str) -> None:
        """Adds a unique member to the susu group."""
        if self.is_started:
            raise RuntimeError("Cannot add members after the group has started.")
        if not member_id or not member_id.strip():
            raise ValueError("Member ID cannot be empty.")
        if member_id in self.members:
            raise ValueError(f"Member '{member_id}' already exists in the group.")
        
        self.members.append(member_id)
        # Initialize contribution tracking for week 1 for the new member
        self.contributions[1][member_id] = Decimal('0.00')

    def record_contribution(self, member_id: str, amount: Union[str, float, Decimal], week: Optional[int] = None) -> None:
        """Records a contribution for a member for a given week. Partial payments allowed."""
        if not self.members:
            raise RuntimeError("Cannot record contributions without members.")
        
        self.is_started = True
        target_week = week if week is not None else self.current_week

        if target_week != self.current_week:
            raise ValueError(f"Can only record contributions for the current week ({self.current_week}).")

        if member_id not in self.members:
            raise KeyError(f"Unknown member: '{member_id}'.")

        dec_amount = Decimal(str(amount)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        if dec_amount <= 0:
            raise ValueError("Contribution amount must be greater than zero.")

        current_paid = self.contributions[target_week].get(member_id, Decimal('0.00'))
        new_total_paid = current_paid + dec_amount

        if new_total_paid > self.weekly_contribution:
            max_allowed = self.weekly_contribution - current_paid
            raise ValueError(
                f"Payment exceeds amount owed for week {target_week}. "
                f"Member still owes {max_allowed:.2f}."
            )

        self.contributions[target_week][member_id] = new_total_paid

    def get_week_status(self, week: Optional[int] = None) -> Dict[str, Any]:
        """Returns who has paid in full, who owes what, and whether the week can close."""
        target_week = week if week is not None else self.current_week
        week_records = self.contributions.get(target_week, {})

        paid_in_full = []
        owes = {}

        for member in self.members:
            paid = week_records.get(member, Decimal('0.00'))
            remaining = self.weekly_contribution - paid
            if remaining == 0:
                paid_in_full.append(member)
            else:
                owes[member] = remaining

        can_close = len(owes) == 0 and len(self.members) > 0
        return {
            "week": target_week,
            "paid_in_full": paid_in_full,
            "owes": owes,
            "can_close": can_close
        }

    def close_week(self) -> Dict[str, Any]:
        """Closes the current week if all members have paid in full and disburses the pot."""
        status = self.get_week_status(self.current_week)
        if not status["can_close"]:
            outstanding_str = ", ".join([f"{m} owes {amt:.2f}" for m, amt in status["owes"].items()])
            raise RuntimeError(f"Cannot close week {self.current_week}. Outstanding balances: {outstanding_str}")

        # Determine recipient based on join order (one member per week, cycling or ending when rounds complete)
        recipient_index = (self.current_week - 1) % len(self.members)
        recipient = self.members[recipient_index]
        total_pot = self.weekly_contribution * len(self.members)

        payout_record = {
            "week": self.current_week,
            "recipient": recipient,
            "amount": total_pot
        }
        self.payout_history.append(payout_record)

        # Move to next week
        self.current_week += 1
        self.contributions[self.current_week] = {m: Decimal('0.00') for m in self.members}

        return payout_record

    def generate_report(self) -> Dict[str, Any]:
        """Shows current week status, payment breakdowns, and payout history."""
        status = self.get_week_status(self.current_week)
        return {
            "current_week": self.current_week,
            "weekly_contribution": self.weekly_contribution,
            "members": self.members,
            "paid_in_full": status["paid_in_full"],
            "owes": {m: float(amt) for m, amt in status["owes"].items()},
            "payout_history": self.payout_history
        }