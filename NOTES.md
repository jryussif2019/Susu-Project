from susu import SusuGroup

# 1. Create a Susu group with 50.00 GHS weekly contribution
susu = SusuGroup(50.00)

# 2. Add members
for name in ["Ama", "Kofi", "Esi"]:
    susu.add_member(name)

# 3. Record contributions (including a partial payment for Esi)
susu.record_contribution("Ama", 50.00)
susu.record_contribution("Kofi", 50.00)
susu.record_contribution("Esi", 30.00)

# Check status
print(susu.get_week_status()) 
# Output shows Esi owes 20.00 and can_close = False

# Complete Esi's payment
susu.record_contribution("Esi", 20.00)

# Close week 1 and disburse pot to Ama
payout = susu.close_week()
print(payout) 
# {'week': 1, 'recipient': 'Ama', 'amount': Decimal('150.00')}