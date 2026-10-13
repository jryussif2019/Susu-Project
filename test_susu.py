import pytest
from decimal import Decimal
from susu import SusuGroup

def test_group_initialization_and_validation():
    with pytest.raises(ValueError):
        SusuGroup(0)
    with pytest.raises(ValueError):
        SusuGroup(-50)

def test_add_members_and_duplicates():
    group = SusuGroup(50.00)
    group.add_member("Ama")
    group.add_member("Kofi")
    
    with pytest.raises(ValueError):
        group.add_member("Ama")  # Duplicate
    with pytest.raises(ValueError):
        group.add_member("")     # Empty ID

def test_partial_payment_and_week_cannot_close():
    group = SusuGroup(50.00)
    for name in ["Ama", "Kofi", "Esi"]:
        group.add_member(name)

    group.record_contribution("Ama", 50.00)
    group.record_contribution("Kofi", 50.00)
    group.record_contribution("Esi", 30.00)  # Partial payment

    status = group.get_week_status()
    assert status["can_close"] is False
    assert status["owes"]["Esi"] == Decimal('20.00')

    # Attempting to close week with outstanding balance should fail
    with pytest.raises(RuntimeError):
        group.close_week()

def test_successful_week_closure_and_payout():
    group = SusuGroup(50.00)
    for name in ["Ama", "Kofi", "Esi"]:
        group.add_member(name)

    group.record_contribution("Ama", 50.00)
    group.record_contribution("Kofi", 50.00)
    group.record_contribution("Esi", 30.00)
    
    # Complete Esi's payment
    group.record_contribution("Esi", 20.00)
    
    # Now week 1 should close successfully and pay out to Ama (index 0)
    payout = group.close_week()
    assert payout["recipient"] == "Ama"
    assert payout["amount"] == Decimal('150.00')
    assert group.current_week == 2

def test_overpayment_validation():
    group = SusuGroup(50.00)
    group.add_member("Ama")
    group.record_contribution("Ama", 30.00)

    # Paying more than remaining balance (30 + 30 = 60 > 50)
    with pytest.raises(ValueError):
        group.record_contribution("Ama", 30.00)

def test_unknown_member_validation():
    group = SusuGroup(50.00)
    group.add_member("Ama")
    
    with pytest.raises(KeyError):
        group.record_contribution("Kwame", 50.00)

def test_add_member_after_start_fails():
    group = SusuGroup(50.00)
    group.add_member("Ama")
    group.record_contribution("Ama", 10.00)

    with pytest.raises(RuntimeError):
        group.add_member("Kofi")