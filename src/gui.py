#!/usr/bin/env python3
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import FuncFormatter

# This must match your simulator file
from simulator import SimulationParams, simulate_scenario


class MortgageSimulatorApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Mortgage vs Invest Simulator")
        self.geometry("900x650")

        self._build_ui()

    # ------------------------
    # UI construction
    # ------------------------
    def _build_ui(self) -> None:
        # Main layout: left controls, right results/plot
        left = ttk.Frame(self, padding=10)
        left.pack(side=tk.LEFT, fill=tk.Y)

        right = ttk.Frame(self, padding=10)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # --- Left panel: inputs ---
        ttk.Label(
            left,
            text="Simulation Inputs",
            font=("TkDefaultFont", 12, "bold"),
        ).pack(anchor="w", pady=(0, 5))

        self.cash_var = tk.StringVar(value="300000")
        self.price_var = tk.StringVar(value="450000")
        self.taxes_var = tk.StringVar(value="10")
        self.mortgage_rate_var = tk.StringVar(value="3.5")
        self.mortgage_years_var = tk.StringVar(value="30")
        self.invest_return_var = tk.StringVar(value="7")
        self.prop_appreciation_var = tk.StringVar(value="2")

        # Custom downpayment AMOUNT (currency)
        self.downpayment_custom_var = tk.StringVar(value="60000")

        def add_labeled_entry(parent, label, var):
            frame = ttk.Frame(parent)
            frame.pack(fill=tk.X, pady=2)
            ttk.Label(frame, text=label, width=26, anchor="w").pack(side=tk.LEFT)
            entry = ttk.Entry(frame, textvariable=var, width=12)
            entry.pack(side=tk.LEFT)
            return entry

        add_labeled_entry(left, "Cash available", self.cash_var)
        add_labeled_entry(left, "Property price", self.price_var)
        add_labeled_entry(left, "Taxes % of property", self.taxes_var)
        add_labeled_entry(left, "Mortgage APR %", self.mortgage_rate_var)
        add_labeled_entry(left, "Mortgage years", self.mortgage_years_var)
        add_labeled_entry(left, "Investment return %", self.invest_return_var)
        add_labeled_entry(left, "Property appreciation %", self.prop_appreciation_var)

        ttk.Separator(left, orient="horizontal").pack(fill=tk.X, pady=8)

        # Custom downpayment amount
        ttk.Label(
            left,
            text="Downpayment amount (currency)",
            font=("TkDefaultFont", 10, "bold"),
        ).pack(anchor="w")

        custom_frame = ttk.Frame(left)
        custom_frame.pack(anchor="w", pady=(4, 0))

        ttk.Entry(
            custom_frame,
            textvariable=self.downpayment_custom_var,
            width=12,
        ).pack(side=tk.LEFT, padx=3)

        ttk.Button(
            custom_frame,
            text="Run simulation",
            command=self.run_custom_simulation,
        ).pack(side=tk.LEFT, padx=5)

        # --- Right panel: results + plot ---
        top_right = ttk.Frame(right)
        top_right.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(
            top_right,
            text="Simulation Results",
            font=("TkDefaultFont", 12, "bold"),
        ).pack(anchor="w")

        # Results table: Metric | Value
        self.results_tree = ttk.Treeview(
            top_right,
            columns=("metric", "value"),
            show="headings",
            height=10,
        )

        self.results_tree.heading("metric", text="Metric")
        self.results_tree.heading("value", text="Value")

        self.results_tree.column("metric", width=320, anchor="w")
        self.results_tree.column("value", width=200, anchor="e")

        self.results_tree.pack(fill=tk.X, pady=4)

        self.result_labels = {
            "monthly_payment": "Monthly mortgage payment",
            "total_property_cost": "Purchase cost incl. taxes",
            "downpayment": "Downpayment",
            "initial_investment": "Initial investment (cash leftover)",
            "mortgage_principal": "Mortgage principal financed",
            "interest_paid": "Total interest paid",
            "total_paid": "Total out-of-pocket paid",
            "final_property_value": "Final property value",
            "final_investment_value": "Final investment value",
        }

        # Create blank rows
        for key, label in self.result_labels.items():
            self.results_tree.insert("", tk.END, iid=key, values=(label, "$0.00"))

        # Summary text under the table
        self.summary_var = tk.StringVar(
            value="Run a simulation to see a summary of your scenario here."
        )
        self.summary_label = ttk.Label(
            top_right,
            textvariable=self.summary_var,
            wraplength=550,
            justify="left",
        )
        self.summary_label.pack(fill=tk.X, pady=(6, 4))

        # Plot
        fig = Figure(figsize=(5, 3), dpi=100)
        self.ax = fig.add_subplot(111)

        self.ax.yaxis.set_major_formatter(
            FuncFormatter(lambda x, p: f"${x:,.0f}")
        )
        self.ax.set_ylabel("Amount")
        self.ax.set_title("Simulation breakdown")

        self.canvas = FigureCanvasTkAgg(fig, master=right)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, pady=(8, 0))

    # ------------------------
    # Helpers
    # ------------------------
    def _format_money(self, value: float) -> str:
        return f"${value:,.2f}"

    # Optional helper if you later want percent formatting
    def _format_percent(self, value: float) -> str:
        return f"{value:.1f}%"

    def _get_params_from_ui(self) -> SimulationParams | None:
        try:
            cash = float(self.cash_var.get())
            price = float(self.price_var.get())
            taxes_pct = float(self.taxes_var.get())
            mortgage_rate = float(self.mortgage_rate_var.get())
            mortgage_years = int(float(self.mortgage_years_var.get()))
            invest_return = float(self.invest_return_var.get())
            prop_app = float(self.prop_appreciation_var.get())
        except ValueError:
            messagebox.showerror("Invalid input", "Please check your numeric inputs.")
            return None

        return SimulationParams(
            cash_available=cash,
            property_price=price,
            taxes_pct=taxes_pct,
            mortgage_rate_annual_pct=mortgage_rate,
            mortgage_years=mortgage_years,
            investment_return_annual_pct=invest_return,
            property_appreciation_annual_pct=prop_app,
        )

    # ------------------------
    # Simulation trigger
    # ------------------------
    def run_custom_simulation(self) -> None:
        params = self._get_params_from_ui()
        if params is None:
            return

        try:
            downpayment_amount = float(self.downpayment_custom_var.get())
        except ValueError:
            messagebox.showerror(
                "Invalid input",
                "Downpayment amount must be a number.",
            )
            return

        if downpayment_amount <= 0:
            messagebox.showerror(
                "Invalid downpayment",
                "Downpayment must be greater than zero.",
            )
            return

        result = simulate_scenario(params, downpayment_amount)
        self.update_results_table(result)
        self.update_plot(result, params)
        self.update_summary(result, params)

    # ------------------------
    # UI updates
    # ------------------------
    def update_results_table(self, result) -> None:
        for field, label in self.result_labels.items():
            if hasattr(result, field):
                value = getattr(result, field)
                display = (
                    self._format_money(value)
                    if isinstance(value, float)
                    else str(value)
                )
            else:
                display = "N/A"

            self.results_tree.item(
                field,
                values=(label, display),
            )

    def update_plot(self, result, params: SimulationParams) -> None:
        labels = [
            "Downpayment",
            "Initial investment",
            "Interest paid",
            "Total paid",
            "Final property",
            "Final investment",
        ]
        values = [
            result.downpayment,
            result.initial_investment,
            result.interest_paid,
            result.total_paid,
            result.final_property_value,
            result.final_investment_value,
        ]

        self.ax.clear()
        self.ax.yaxis.set_major_formatter(
            FuncFormatter(lambda x, p: f"${x:,.0f}")
        )
        self.ax.bar(labels, values)
        self.ax.set_ylabel("Amount")

        pct = 0.0
        if params.property_price > 0:
            pct = result.downpayment / params.property_price * 100.0

        self.ax.set_title(
            f"Downpayment: {self._format_money(result.downpayment)} "
            f"({pct:.1f}% of price)"
        )
        self.ax.tick_params(axis="x", rotation=20)

        self.canvas.draw()

    def update_summary(self, result, params: SimulationParams) -> None:
        """Build a human-readable explanation of the simulation."""
        cash = self._format_money(params.cash_available)
        price = self._format_money(params.property_price)
        total_cost = self._format_money(result.total_property_cost)
        down = self._format_money(result.downpayment)

        dp_pct = 0.0
        if params.property_price > 0:
            dp_pct = result.downpayment / params.property_price * 100.0

        leftover_invest = self._format_money(result.initial_investment)
        mortgage_principal = self._format_money(result.mortgage_principal)
        monthly = self._format_money(result.monthly_payment)
        interest_paid = self._format_money(result.interest_paid)
        total_paid = self._format_money(result.total_paid)
        final_prop = self._format_money(result.final_property_value)
        final_inv = self._format_money(result.final_investment_value)
        total_assets_value = self._format_money(
            result.final_property_value + result.final_investment_value
        )

        text = (
            f"You start with {cash} in cash.\n\n"
            f"You buy a property with a listing price of {price}, which becomes "
            f"{total_cost} once taxes and other upfront costs are included.\n\n"
            f"You decide to put {down} down ({dp_pct:.1f}% of the property price), "
            f"leaving {leftover_invest} available to invest.\n\n"
            f"This leaves a mortgage principal of {mortgage_principal} with a "
            f"monthly payment of {monthly}.\n\n"
            f"Over the life of the mortgage you pay {interest_paid} in interest, "
            f"for a total of {total_paid} paid out of pocket "
            f"(downpayment + all mortgage payments).\n\n"
            f"At the end of the simulation period, the property is worth {final_prop} "
            f"and your investments have grown to {final_inv}, giving you a combined "
            f"asset value of {total_assets_value}."
        )

        self.summary_var.set(text)


def main() -> None:
    app = MortgageSimulatorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
