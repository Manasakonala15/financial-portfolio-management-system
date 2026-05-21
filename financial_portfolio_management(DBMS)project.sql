-- =====================================================
-- FINANCIAL PORTFOLIO MANAGEMENT SYSTEM
-- =====================================================

DROP DATABASE IF EXISTS wealth_portfolio_management;
CREATE DATABASE wealth_portfolio_management;
USE wealth_portfolio_management;

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE asset_categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE assets (
    asset_id INT AUTO_INCREMENT PRIMARY KEY,
    asset_name VARCHAR(100) NOT NULL,
    asset_type VARCHAR(50) NOT NULL,
    category_id INT NOT NULL,
    FOREIGN KEY (category_id)
        REFERENCES asset_categories(category_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE risk_profiles (
    risk_id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT NOT NULL,
    risk_level ENUM('Low','Medium','High') NOT NULL,
    FOREIGN KEY (category_id)
        REFERENCES asset_categories(category_id)
        ON DELETE CASCADE
);

CREATE TABLE portfolio (
    portfolio_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    asset_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    buy_price DECIMAL(12,2) NOT NULL,
    buy_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE,
    FOREIGN KEY (asset_id)
        REFERENCES assets(asset_id)
        ON DELETE CASCADE
);

CREATE TABLE brokers (
    broker_id INT AUTO_INCREMENT PRIMARY KEY,
    broker_name VARCHAR(100) NOT NULL,
    contact_info VARCHAR(100)
);

CREATE TABLE transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    portfolio_id INT NOT NULL,
    transaction_type ENUM('BUY','SELL') NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(12,2) NOT NULL,
    transaction_date DATE NOT NULL,
    broker_id INT,
    FOREIGN KEY (portfolio_id)
        REFERENCES portfolio(portfolio_id)
        ON DELETE CASCADE,
    FOREIGN KEY (broker_id)
        REFERENCES brokers(broker_id)
        ON DELETE SET NULL
);

CREATE TABLE asset_prices (
    price_id INT AUTO_INCREMENT PRIMARY KEY,
    asset_id INT NOT NULL,
    price DECIMAL(12,2) NOT NULL,
    price_date DATE NOT NULL,
    FOREIGN KEY (asset_id)
        REFERENCES assets(asset_id)
        ON DELETE CASCADE
);

CREATE INDEX idx_asset_price_date ON asset_prices(asset_id, price_date);
CREATE INDEX idx_portfolio_user ON portfolio(user_id);
CREATE INDEX idx_transaction_date ON transactions(transaction_date);

CREATE VIEW portfolio_summary_view AS
SELECT 
    u.user_id,
    u.name AS user_name,
    a.asset_name,
    a.asset_type,
    c.category_name,
    rp.risk_level,
    p.quantity,
    p.buy_price,
    ap.price AS current_price,
    (p.quantity * p.buy_price) AS investment,
    (p.quantity * ap.price) AS current_value,
    ((ap.price - p.buy_price) * p.quantity) AS profit,
    ROUND(((ap.price - p.buy_price) / p.buy_price) * 100, 2) AS return_percent
FROM portfolio p
JOIN users u ON p.user_id = u.user_id
JOIN assets a ON p.asset_id = a.asset_id
JOIN asset_categories c ON a.category_id = c.category_id
LEFT JOIN risk_profiles rp ON c.category_id = rp.category_id
JOIN asset_prices ap ON a.asset_id = ap.asset_id
WHERE ap.price_date = (
    SELECT MAX(price_date)
    FROM asset_prices
    WHERE asset_id = a.asset_id
);

DELIMITER //

CREATE PROCEDURE GetPortfolioSummary(IN uid INT)
BEGIN
    SELECT 
        SUM(investment) AS total_investment,
        SUM(current_value) AS current_value,
        SUM(profit) AS total_profit,
        ROUND((SUM(profit)/SUM(investment))*100,2) AS return_percentage
    FROM portfolio_summary_view
    WHERE user_id = uid;
END //

CREATE PROCEDURE GetAssetPerformance()
BEGIN
    SELECT 
        asset_name,
        SUM(profit) AS total_profit
    FROM portfolio_summary_view
    GROUP BY asset_name
    ORDER BY total_profit DESC;
END //

CREATE TRIGGER after_portfolio_insert
AFTER INSERT ON portfolio
FOR EACH ROW
BEGIN
    INSERT INTO transactions (
        portfolio_id,
        transaction_type,
        quantity,
        price,
        transaction_date
    )
    VALUES (
        NEW.portfolio_id,
        'BUY',
        NEW.quantity,
        NEW.buy_price,
        CURDATE()
    );
END //

DELIMITER ;

INSERT INTO users (name, email, password)
VALUES ('Manasa', 'manasa@gmail.com', '1234');

INSERT INTO asset_categories (category_name) VALUES
('Stock'), ('Bond'), ('Real Estate'), ('Mutual Fund'), ('Commodity');

INSERT INTO risk_profiles (category_id, risk_level) VALUES
(1, 'High'),
(2, 'Low'),
(3, 'Medium'),
(4, 'Medium'),
(5, 'High');

INSERT INTO assets (asset_name, asset_type, category_id) VALUES
('TCS', 'Equity', 1),
('Infosys', 'Equity', 1),
('HDFC Bond', 'Corporate Bond', 2),
('Govt Bond', 'Government Bond', 2),
('DLF Ltd', 'Real Estate', 3),
('SBI Mutual Fund', 'Open-Ended Fund', 4),
('Gold ETF', 'Commodity ETF', 5);

INSERT INTO brokers (broker_name, contact_info) VALUES
('Zerodha', 'contact@zerodha.com'),
('ICICI Direct', 'support@icicidirect.com');

INSERT INTO portfolio (user_id, asset_id, quantity, buy_price, buy_date) VALUES
(1,1,10,3500,'2024-01-10'),
(1,2,20,3000,'2024-01-15'),
(1,3,50,1000,'2024-02-10'),
(1,4,30,1200,'2024-02-20'),
(1,5,2,55000,'2024-03-01'),
(1,6,100,500,'2024-03-10'),
(1,7,4,2500,'2024-04-01');

INSERT INTO asset_prices (asset_id, price, price_date) VALUES
(1,4100,'2024-04-01'),
(2,3500,'2024-04-01'),
(3,1100,'2024-04-01'),
(4,1250,'2024-04-01'),
(5,58000,'2024-04-01'),
(6,620,'2024-04-01'),
(7,2700,'2024-04-01');

INSERT INTO transactions 
(portfolio_id, transaction_type, quantity, price, transaction_date, broker_id)
VALUES
(1,'BUY',10,3500,'2024-01-10',1),
(2,'BUY',20,3000,'2024-01-15',1),
(3,'BUY',50,1000,'2024-02-10',2),
(4,'BUY',30,1200,'2024-02-20',2),
(5,'BUY',2,55000,'2024-03-01',1),
(6,'BUY',100,500,'2024-03-10',2),
(7,'BUY',4,2500,'2024-04-01',2);
