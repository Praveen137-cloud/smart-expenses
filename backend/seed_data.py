"""Seed default sample categories, users, transactions and budgets."""
from datetime import date
from decimal import Decimal
import logging
from sqlalchemy.orm import Session
from backend.models import User, Category, Transaction, Budget

logger = logging.getLogger("expense_tracker.seed")

SAMPLE_USERS = [
    {"id": 1, "name": "Demo Student", "email": "demo@example.com", "password": "demo_no_login"},
    {"id": 2, "name": "Test User", "email": "test@example.com", "password": "demo_no_login"},
]

SAMPLE_CATEGORIES = [
    {"id": 1, "name": "Food", "description": "Restaurants, coffee, groceries"},
    {"id": 2, "name": "Transit", "description": "Cabs, metro, bus, fuel"},
    {"id": 3, "name": "Utilities", "description": "Electricity, water, internet, recharge"},
    {"id": 4, "name": "Shopping", "description": "Online and offline shopping"},
    {"id": 5, "name": "Entertainment", "description": "Movies, games, events"},
    {"id": 6, "name": "Healthcare", "description": "Pharmacy, doctor, hospital"},
    {"id": 7, "name": "Education", "description": "Books, courses, fees"},
    {"id": 8, "name": "Housing", "description": "Rent and maintenance"},
    {"id": 9, "name": "Subscriptions", "description": "Streaming and recurring plans"},
    {"id": 10, "name": "Other", "description": "Everything else"},
]

SAMPLE_TRANSACTIONS = [
    (1, 1, 'Starbucks Coffee', 250.00, date(2026, 10, 1), 'UPI', 'Food', 0.9312),
    (1, 1, 'McDonalds Lunch', 420.00, date(2026, 10, 2), 'Debit Card', 'Food', 0.9101),
    (1, 1, 'Swiggy Food Order', 560.00, date(2026, 10, 3), 'UPI', 'Food', 0.9644),
    (1, 1, 'Zomato Dinner', 780.00, date(2026, 10, 4), 'UPI', 'Food', 0.9520),
    (1, 1, 'Walmart Groceries', 1850.00, date(2026, 10, 5), 'Credit Card', 'Food', 0.8870),
    (1, 1, 'Big Bazaar Vegetables', 940.00, date(2026, 10, 6), 'Cash', 'Food', 0.7421),
    (1, 1, 'Dominos Pizza', 690.00, date(2026, 10, 7), 'UPI', 'Food', 0.9033),
    (1, 1, 'Cafe Coffee Day', 320.00, date(2026, 10, 8), 'Cash', 'Food', 0.9210),
    (1, 1, 'Biryani Restaurant', 880.00, date(2026, 10, 8), 'Debit Card', 'Food', 0.8814),
    (1, 2, 'Uber Ride', 320.00, date(2026, 10, 1), 'UPI', 'Transit', 0.9450),
    (1, 2, 'Ola Cab', 280.00, date(2026, 10, 2), 'UPI', 'Transit', 0.9388),
    (1, 2, 'Metro Ticket', 120.00, date(2026, 10, 3), 'Cash', 'Transit', 0.9120),
    (1, 2, 'Bus Ticket', 60.00, date(2026, 10, 4), 'Cash', 'Transit', 0.9005),
    (1, 2, 'Petrol Pump Fuel', 1200.00, date(2026, 10, 6), 'Credit Card', 'Transit', 0.8602),
    (1, 3, 'Electricity Bill', 1250.00, date(2026, 10, 2), 'Net Banking', 'Utilities', 0.9733),
    (1, 3, 'Water Bill', 380.00, date(2026, 10, 3), 'UPI', 'Utilities', 0.9681),
    (1, 3, 'Internet Bill', 999.00, date(2026, 10, 4), 'Net Banking', 'Utilities', 0.9590),
    (1, 3, 'Mobile Recharge', 399.00, date(2026, 10, 5), 'UPI', 'Utilities', 0.9244),
    (1, 4, 'Amazon Shopping', 2300.00, date(2026, 10, 3), 'Credit Card', 'Shopping', 0.9477),
    (1, 4, 'Clothes Purchase', 1799.00, date(2026, 10, 5), 'Debit Card', 'Shopping', 0.9012),
    (1, 4, 'Flipkart Headphones', 1499.00, date(2026, 10, 7), 'UPI', 'Shopping', 0.9366),
    (1, 5, 'Movie Ticket', 450.00, date(2026, 10, 4), 'UPI', 'Entertainment', 0.9521),
    (1, 5, 'Cinema Snacks', 300.00, date(2026, 10, 4), 'Cash', 'Entertainment', 0.5120),
    (1, 5, 'Gaming Credits', 500.00, date(2026, 10, 6), 'UPI', 'Entertainment', 0.8804),
    (1, 6, 'Apollo Pharmacy', 780.00, date(2026, 10, 2), 'UPI', 'Healthcare', 0.9655),
    (1, 6, 'Doctor Consultation', 600.00, date(2026, 10, 5), 'Cash', 'Healthcare', 0.9433),
    (1, 7, 'College Books', 1200.00, date(2026, 10, 1), 'Debit Card', 'Education', 0.9710),
    (1, 7, 'Udemy Course', 449.00, date(2026, 10, 3), 'Credit Card', 'Education', 0.9588),
    (1, 7, 'Exam Fee', 800.00, date(2026, 10, 6), 'Net Banking', 'Education', 0.9317),
    (1, 8, 'House Rent', 12000.00, date(2026, 10, 1), 'Net Banking', 'Housing', 0.9802),
    (1, 9, 'Netflix Subscription', 649.00, date(2026, 10, 2), 'Credit Card', 'Subscriptions', 0.9761),
    (1, 9, 'Spotify Premium', 119.00, date(2026, 10, 2), 'UPI', 'Subscriptions', 0.9690),
    (1, 10, 'Charity Donation', 500.00, date(2026, 10, 5), 'Cash', 'Other', 0.8120),
    (1, 10, 'Gift for Friend', 1100.00, date(2026, 10, 7), 'UPI', 'Other', 0.7733),
    # previous month
    (1, 1, 'Starbucks Coffee', 300.00, date(2026, 9, 12), 'UPI', 'Food', 0.9312),
    (1, 2, 'Uber Ride', 350.00, date(2026, 9, 15), 'UPI', 'Transit', 0.9450),
    (1, 1, 'Swiggy Food Order', 600.00, date(2026, 9, 18), 'UPI', 'Food', 0.9644),
    (1, 8, 'House Rent', 12000.00, date(2026, 9, 1), 'Net Banking', 'Housing', 0.9802),
    (1, 9, 'Netflix Subscription', 649.00, date(2026, 9, 2), 'Credit Card', 'Subscriptions', 0.9761),
    (1, 3, 'Electricity Bill', 1180.00, date(2026, 9, 5), 'Net Banking', 'Utilities', 0.9733),
]

SAMPLE_BUDGETS = [
    (1, 1, 10, 2026, 7000.00),
    (1, 2, 10, 2026, 3000.00),
    (1, 3, 10, 2026, 3000.00),
    (1, 4, 10, 2026, 4500.00),
    (1, 5, 10, 2026, 2000.00),
    (1, 6, 10, 2026, 2000.00),
    (1, 7, 10, 2026, 3000.00),
    (1, 8, 10, 2026, 13000.00),
    (1, 9, 10, 2026, 1000.00),
    (1, 1, 9, 2026, 6000.00),
    (1, 8, 9, 2026, 13000.00),
    (1, 2, 9, 2026, 2500.00),
]


def seed_database(db: Session):
    """Seed sample data if the categories table is empty."""
    if db.query(Category).first() is not None:
        return

    logger.info("Seeding initial database data...")

    # Seed users
    for u in SAMPLE_USERS:
        if not db.query(User).filter(User.id == u["id"]).first():
            db.add(User(**u))
    db.flush()

    # Seed categories
    for c in SAMPLE_CATEGORIES:
        if not db.query(Category).filter(Category.id == c["id"]).first():
            db.add(Category(**c))
    db.flush()

    # Seed transactions
    for tx in SAMPLE_TRANSACTIONS:
        db.add(Transaction(
            user_id=tx[0],
            category_id=tx[1],
            description=tx[2],
            amount=Decimal(str(tx[3])),
            transaction_date=tx[4],
            payment_method=tx[5],
            predicted_category=tx[6],
            prediction_confidence=Decimal(str(tx[7])),
        ))

    # Seed budgets
    for b in SAMPLE_BUDGETS:
        db.add(Budget(
            user_id=b[0],
            category_id=b[1],
            month=b[2],
            year=b[3],
            budget_amount=Decimal(str(b[4])),
        ))

    db.commit()
    logger.info("Database seeding complete.")
