-- Smart Expense & Personal Finance Tracker - MySQL 8+
-- WARNING: re-running this script drops and recreates the tables (resets sample data).
CREATE DATABASE IF NOT EXISTS finance_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE finance_db;

SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS budgets;
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS users;
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE users (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    email       VARCHAR(150) NOT NULL UNIQUE,
    password    VARCHAR(255) NOT NULL,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE categories (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    name         VARCHAR(50) NOT NULL UNIQUE,
    description  VARCHAR(255)
) ENGINE=InnoDB;

CREATE TABLE transactions (
    id                     INT AUTO_INCREMENT PRIMARY KEY,
    user_id                INT NOT NULL,
    category_id            INT NOT NULL,
    description            VARCHAR(255) NOT NULL,
    amount                 DECIMAL(10,2) NOT NULL,
    transaction_date       DATE NOT NULL,
    payment_method         VARCHAR(30) NOT NULL DEFAULT 'Cash',
    predicted_category     VARCHAR(50) NULL,
    prediction_confidence  DECIMAL(5,4) NULL,
    notes                  TEXT NULL,
    created_at             TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_tx_user     FOREIGN KEY (user_id)     REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_tx_category FOREIGN KEY (category_id) REFERENCES categories(id),
    CONSTRAINT chk_tx_amount  CHECK (amount > 0),
    INDEX idx_tx_user_date (user_id, transaction_date),
    INDEX idx_tx_category (category_id)
) ENGINE=InnoDB;

CREATE TABLE budgets (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    user_id        INT NOT NULL,
    category_id    INT NOT NULL,
    month          TINYINT NOT NULL,
    year           SMALLINT NOT NULL,
    budget_amount  DECIMAL(10,2) NOT NULL,
    created_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_bud_user     FOREIGN KEY (user_id)     REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_bud_category FOREIGN KEY (category_id) REFERENCES categories(id),
    CONSTRAINT chk_bud_month   CHECK (month BETWEEN 1 AND 12),
    CONSTRAINT chk_bud_amount  CHECK (budget_amount > 0),
    UNIQUE KEY uq_budget (user_id, category_id, month, year)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------- seed data
INSERT INTO users (name, email, password) VALUES
    ('Demo Student', 'demo@example.com', 'demo_no_login'),
    ('Test User',    'test@example.com', 'demo_no_login');

INSERT INTO categories (name, description) VALUES
    ('Food',          'Restaurants, coffee, groceries'),
    ('Transit',       'Cabs, metro, bus, fuel'),
    ('Utilities',     'Electricity, water, internet, recharge'),
    ('Shopping',      'Online and offline shopping'),
    ('Entertainment', 'Movies, games, events'),
    ('Healthcare',    'Pharmacy, doctor, hospital'),
    ('Education',     'Books, courses, fees'),
    ('Housing',       'Rent and maintenance'),
    ('Subscriptions', 'Streaming and recurring plans'),
    ('Other',         'Everything else');

-- category ids: 1 Food, 2 Transit, 3 Utilities, 4 Shopping, 5 Entertainment,
--               6 Healthcare, 7 Education, 8 Housing, 9 Subscriptions, 10 Other
INSERT INTO transactions
    (user_id, category_id, description, amount, transaction_date, payment_method, predicted_category, prediction_confidence)
VALUES
    (1, 1, 'Starbucks Coffee',        250.00, '2026-10-01', 'UPI',         'Food', 0.9312),
    (1, 1, 'McDonalds Lunch',         420.00, '2026-10-02', 'Debit Card',  'Food', 0.9101),
    (1, 1, 'Swiggy Food Order',       560.00, '2026-10-03', 'UPI',         'Food', 0.9644),
    (1, 1, 'Zomato Dinner',           780.00, '2026-10-04', 'UPI',         'Food', 0.9520),
    (1, 1, 'Walmart Groceries',      1850.00, '2026-10-05', 'Credit Card', 'Food', 0.8870),
    (1, 1, 'Big Bazaar Vegetables',   940.00, '2026-10-06', 'Cash',        'Food', 0.7421),
    (1, 1, 'Dominos Pizza',           690.00, '2026-10-07', 'UPI',         'Food', 0.9033),
    (1, 1, 'Cafe Coffee Day',         320.00, '2026-10-08', 'Cash',        'Food', 0.9210),
    (1, 1, 'Biryani Restaurant',      880.00, '2026-10-08', 'Debit Card',  'Food', 0.8814),
    (1, 2, 'Uber Ride',               320.00, '2026-10-01', 'UPI',         'Transit', 0.9450),
    (1, 2, 'Ola Cab',                 280.00, '2026-10-02', 'UPI',         'Transit', 0.9388),
    (1, 2, 'Metro Ticket',            120.00, '2026-10-03', 'Cash',        'Transit', 0.9120),
    (1, 2, 'Bus Ticket',               60.00, '2026-10-04', 'Cash',        'Transit', 0.9005),
    (1, 2, 'Petrol Pump Fuel',       1200.00, '2026-10-06', 'Credit Card', 'Transit', 0.8602),
    (1, 3, 'Electricity Bill',       1250.00, '2026-10-02', 'Net Banking', 'Utilities', 0.9733),
    (1, 3, 'Water Bill',              380.00, '2026-10-03', 'UPI',         'Utilities', 0.9681),
    (1, 3, 'Internet Bill',           999.00, '2026-10-04', 'Net Banking', 'Utilities', 0.9590),
    (1, 3, 'Mobile Recharge',         399.00, '2026-10-05', 'UPI',         'Utilities', 0.9244),
    (1, 4, 'Amazon Shopping',        2300.00, '2026-10-03', 'Credit Card', 'Shopping', 0.9477),
    (1, 4, 'Clothes Purchase',       1799.00, '2026-10-05', 'Debit Card',  'Shopping', 0.9012),
    (1, 4, 'Flipkart Headphones',    1499.00, '2026-10-07', 'UPI',         'Shopping', 0.9366),
    (1, 5, 'Movie Ticket',            450.00, '2026-10-04', 'UPI',         'Entertainment', 0.9521),
    (1, 5, 'Cinema Snacks',           300.00, '2026-10-04', 'Cash',        'Entertainment', 0.5120),
    (1, 5, 'Gaming Credits',          500.00, '2026-10-06', 'UPI',         'Entertainment', 0.8804),
    (1, 6, 'Apollo Pharmacy',         780.00, '2026-10-02', 'UPI',         'Healthcare', 0.9655),
    (1, 6, 'Doctor Consultation',     600.00, '2026-10-05', 'Cash',        'Healthcare', 0.9433),
    (1, 7, 'College Books',          1200.00, '2026-10-01', 'Debit Card',  'Education', 0.9710),
    (1, 7, 'Udemy Course',            449.00, '2026-10-03', 'Credit Card', 'Education', 0.9588),
    (1, 7, 'Exam Fee',                800.00, '2026-10-06', 'Net Banking', 'Education', 0.9317),
    (1, 8, 'House Rent',            12000.00, '2026-10-01', 'Net Banking', 'Housing', 0.9802),
    (1, 9, 'Netflix Subscription',    649.00, '2026-10-02', 'Credit Card', 'Subscriptions', 0.9761),
    (1, 9, 'Spotify Premium',         119.00, '2026-10-02', 'UPI',         'Subscriptions', 0.9690),
    (1, 10, 'Charity Donation',       500.00, '2026-10-05', 'Cash',        'Other', 0.8120),
    (1, 10, 'Gift for Friend',       1100.00, '2026-10-07', 'UPI',         'Other', 0.7733),
    -- previous month
    (1, 1, 'Starbucks Coffee',        300.00, '2026-09-12', 'UPI',         'Food', 0.9312),
    (1, 2, 'Uber Ride',               350.00, '2026-09-15', 'UPI',         'Transit', 0.9450),
    (1, 1, 'Swiggy Food Order',       600.00, '2026-09-18', 'UPI',         'Food', 0.9644),
    (1, 8, 'House Rent',            12000.00, '2026-09-01', 'Net Banking', 'Housing', 0.9802),
    (1, 9, 'Netflix Subscription',    649.00, '2026-09-02', 'Credit Card', 'Subscriptions', 0.9761),
    (1, 3, 'Electricity Bill',       1180.00, '2026-09-05', 'Net Banking', 'Utilities', 0.9733);

INSERT INTO budgets (user_id, category_id, month, year, budget_amount) VALUES
    (1, 1, 10, 2026,  7000.00),
    (1, 2, 10, 2026,  3000.00),
    (1, 3, 10, 2026,  3000.00),
    (1, 4, 10, 2026,  4500.00),
    (1, 5, 10, 2026,  2000.00),
    (1, 6, 10, 2026,  2000.00),
    (1, 7, 10, 2026,  3000.00),
    (1, 8, 10, 2026, 13000.00),
    (1, 9, 10, 2026,  1000.00),
    (1, 1,  9, 2026,  6000.00),
    (1, 8,  9, 2026, 13000.00),
    (1, 2,  9, 2026,  2500.00);
