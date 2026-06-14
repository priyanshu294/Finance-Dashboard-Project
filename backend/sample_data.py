"""
Sample customer expense data for Personal Finance Advisor.
Provides realistic monthly expense profiles for multiple customers.
"""

# Monthly income and expense data per customer
CUSTOMERS = {
    "Alice": {
        "monthly_income": 75000,
        "expenses": {
            "Food":          12000,
            "Rent":          18000,
            "Shopping":       8500,
            "Travel":         6000,
            "EMI":           10000,
            "Utilities":      3500,
            "Entertainment":  4000,
        },
        "profile": "Mid-career software engineer, single, rents apartment.",
    },
    "Bob": {
        "monthly_income": 55000,
        "expenses": {
            "Food":           9500,
            "Rent":          15000,
            "Shopping":      12000,
            "Travel":         2000,
            "EMI":           12000,
            "Utilities":      3000,
            "Entertainment":  6500,
        },
        "profile": "Marketing executive, high discretionary spending.",
    },
    "Carol": {
        "monthly_income": 95000,
        "expenses": {
            "Food":          14000,
            "Rent":          22000,
            "Shopping":       7000,
            "Travel":        11000,
            "EMI":           15000,
            "Utilities":      4500,
            "Entertainment":  3500,
        },
        "profile": "Senior manager, frequent traveler, home loan EMI.",
    },
    "David": {
        "monthly_income": 40000,
        "expenses": {
            "Food":           8000,
            "Rent":          12000,
            "Shopping":       5000,
            "Travel":         1500,
            "EMI":            6000,
            "Utilities":      2500,
            "Entertainment":  3000,
        },
        "profile": "Junior analyst, careful spender, moderate savings.",
    },
}

# Benchmark ratios: ideal % of income per category
BENCHMARKS = {
    "Food":          0.15,
    "Rent":          0.30,
    "Shopping":      0.10,
    "Travel":        0.08,
    "EMI":           0.20,
    "Utilities":     0.05,
    "Entertainment": 0.05,
}

# Saving tips mapped to overspent categories
SAVING_TIPS = {
    "Food":          [
        "Cook at home at least 4 days a week to cut food costs by ~30%.",
        "Use grocery apps and buy in bulk for non-perishables.",
        "Avoid food delivery apps — the markup is often 40% above restaurant price.",
    ],
    "Rent":          [
        "Consider a flatmate to split rent costs.",
        "Negotiate a 6-month lock-in with your landlord for a discount.",
        "Explore co-living spaces if flexibility is acceptable.",
    ],
    "Shopping":      [
        "Apply the 24-hour rule — wait a day before any non-essential purchase.",
        "Unsubscribe from promotional emails and push notifications.",
        "Set a monthly shopping budget cap and track it in a simple spreadsheet.",
    ],
    "Travel":        [
        "Book flights 6-8 weeks in advance to save up to 25%.",
        "Use reward credit cards for all travel bookings.",
        "Choose staycations or bus/train for short trips.",
    ],
    "EMI":           [
        "Prepay the principal when you receive bonuses to reduce interest burden.",
        "Consolidate multiple loans into a single lower-interest loan.",
        "Avoid adding new EMIs while existing ones are active.",
    ],
    "Utilities":     [
        "Switch to LED bulbs and 5-star rated appliances.",
        "Set ACs to 24°C — each degree below adds ~6% to electricity bills.",
        "Audit unused subscriptions (OTT, gym, etc.) and cancel them.",
    ],
    "Entertainment": [
        "Share streaming subscriptions with family using family plans.",
        "Look for free or discounted events in your city.",
        "Set a monthly entertainment envelope and stick to it.",
    ],
}

DEFAULT_CUSTOMER = "Alice"
