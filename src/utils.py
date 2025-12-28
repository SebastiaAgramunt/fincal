#!/usr/bin/env python3

def ask_float(prompt: str, default: float | None = None) -> float:
    """
    Helper to safely read a float from input() with optional default.
    """
    while True:
        if default is None:
            text = input(f"{prompt}: ").strip()
        else:
            text = input(f"{prompt} [default {default}]: ").strip()
            if text == "":
                return default
        try:
            return float(text)
        except ValueError:
            print("Please enter a valid number.")


def ask_int(prompt: str, default: int | None = None) -> int:
    """
    Helper to safely read an int from input() with optional default.
    """
    while True:
        if default is None:
            text = input(f"{prompt}: ").strip()
        else:
            text = input(f"{prompt} [default {default}]: ").strip()
            if text == "":
                return default
        try:
            return int(text)
        except ValueError:
            print("Please enter a valid integer.")
            
def monthly_rate_from_annual(annual_pct: float) -> float:
    """
    Convert an annual rate in percent (e.g. 7.0) to an effective monthly rate.
    Uses (1 + r_annual) ** (1/12) - 1 for compounding.
    """
    r_annual = annual_pct / 100.0
    return (1.0 + r_annual) ** (1.0 / 12.0) - 1.0


def mortgage_monthly_payment(principal: float, annual_rate_pct: float, years: int) -> float:
    """
    Standard fixed-rate mortgage payment (French amortization).
    principal: loan amount
    annual_rate_pct: APR in percent (e.g. 3.5)
    years: term in years
    """
    if principal <= 0:
        raise ValueError("Mortgage principal must be > 0")

    n = years * 12
    r_month = annual_rate_pct / 100.0 / 12.0

    if r_month == 0:
        return principal / n

    # Payment formula: P = L * r / (1 - (1+r)^-n)
    return principal * r_month / (1.0 - (1.0 + r_month) ** (-n))

