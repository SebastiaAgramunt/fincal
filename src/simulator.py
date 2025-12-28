#!/usr/bin/env python3

from __future__ import annotations
from dataclasses import dataclass

from utils import mortgage_monthly_payment, monthly_rate_from_annual
from utils import ask_float, ask_int

@dataclass
class SimulationParams:
    cash_available: float                          # e.g. 300000.0
    property_price: float                          # e.g. 450000.0
    taxes_pct: float                               # e.g. 10.0 for 10%
    mortgage_rate_annual_pct: float                # e.g. 3.5 for 3.5%
    mortgage_years: int                            # e.g. 30
    investment_return_annual_pct: float = 7.0      # e.g. 7% for average index fund
    property_appreciation_annual_pct: float = 2.0  # e.g. 2%

@dataclass
class ScenarioResult:
    monthly_payment: float = 0.0
    total_property_cost: float = 0.0
    downpayment: float = 0.0
    initial_investment: float = 0.0
    mortgage_principal: float = 0.0
    interest_paid: float = 0.0
    total_paid: float = 0.0
    final_property_value: float = 0.0
    final_investment_value: float = 0.0

def simulate_scenario(
    params: SimulationParams, downpayment: float
) -> ScenarioResult:
    """
    Simulate a buy vs rent scenario with given parameters and downpayment percentage.
    Returns a ScenarioResult dataclass with results.
    """
    
    # Total value of property including taxes
    total_property_cost = params.property_price * (1 + params.taxes_pct / 100.0)
    
    # Total to finance in mortgage
    mortgage_principal = total_property_cost - downpayment
    
    if downpayment > params.cash_available:
        print("Error: Downpayment exceeds available cash.")
        return ScenarioResult(0.0, 0.0, 0.0)
    
    # initial investment is remaining cash after downpayment
    initial_investment = params.cash_available - downpayment
    
    if mortgage_principal <= 0:
        # No mortgage needed: treat as cash purchase + taxes. No payments, all cash left is investment.
        monthly_payment = 0.0
        n_payments = params.mortgage_years * 12
        balance = 0.0
    else:
        monthly_payment = mortgage_monthly_payment(
            principal=mortgage_principal,
            annual_rate_pct=params.mortgage_rate_annual_pct,
            years=params.mortgage_years,
        )
        n_payments = params.mortgage_years * 12
        balance = mortgage_principal

    # Rates
    r_mortgage_month = params.mortgage_rate_annual_pct / 100.0 / 12.0
    r_invest_month = monthly_rate_from_annual(params.investment_return_annual_pct)
    r_property_month = monthly_rate_from_annual(params.property_appreciation_annual_pct)
    
    # initial values
    property_value = params.property_price
    investment_value = initial_investment
    
    # Simulate month by month until mortgage is paid
    for _ in range(n_payments):
        # Mortgage amortization
        if balance > 0:
            interest = balance * r_mortgage_month
            principal_paid = monthly_payment - interest
            balance -= principal_paid
            if balance < 0:
                balance = 0.0

        # Property appreciation
        property_value *= (1.0 + r_property_month)

        # Investment growth
        investment_value *= (1.0 + r_invest_month)

    final_property_value = property_value
    final_investment_value = investment_value
    interest_paid = (monthly_payment * n_payments) - mortgage_principal
    total_paid = monthly_payment * n_payments + downpayment
    
    
    result = ScenarioResult(
        monthly_payment=monthly_payment,
        total_property_cost=total_property_cost,
        downpayment=downpayment,
        initial_investment=initial_investment,
        mortgage_principal=mortgage_principal,
        interest_paid=interest_paid,
        total_paid=total_paid,
        final_property_value=final_property_value,
        final_investment_value=final_investment_value,
    )
    return result
    
    
def main():
    print("Mortgage vs Rent Simulation")
    cash_available = ask_float("Enter available cash for downpayment", 300000.0)
    property_price = ask_float("Enter the property price", 450000.0)
    taxes_pct = ask_float("Enter property taxes percentage", 10.0)
    mortgage_rate_annual_pct = ask_float("Enter mortgage annual interest rate (APR) in %", 3.5)
    mortgage_years = ask_int("Enter mortgage term in years", 30)
    investment_return_annual_pct = ask_float("Enter expected annual investment return in %", 7.0)
    property_appreciation_annual_pct = ask_float("Enter expected annual property appreciation in %", 2.0)

    params = SimulationParams(
        cash_available=cash_available,
        property_price=property_price,
        taxes_pct=taxes_pct,
        mortgage_rate_annual_pct=mortgage_rate_annual_pct,
        mortgage_years=mortgage_years,
        investment_return_annual_pct=investment_return_annual_pct,
        property_appreciation_annual_pct=property_appreciation_annual_pct,
    )

    downpayment = ask_float("Enter downpayment amount", 60000.0)
    result = simulate_scenario(params, downpayment)
    
    # print inputs
    print("\nSimulation Parameters:")
    print("----------------------")
    for field in params.__dataclass_fields__:
        value = getattr(params, field)
        if isinstance(value, float):
            print(f"{field.replace('_', ' ').title()}: ${value:,.2f}")
        else:
            print(f"{field.replace('_', ' ').title()}: {value}")

    print("\nSimulation Results:")
    print("-------------------")
    # print all params in a for loop
    for field in result.__dataclass_fields__:
        value = getattr(result, field)
        if isinstance(value, float):
            print(f"{field.replace('_', ' ').title()}: ${value:,.2f}")
        else:
            print(f"{field.replace('_', ' ').title()}: {value}")
    
    
if __name__ == "__main__":
    main()