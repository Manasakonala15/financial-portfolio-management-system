📊 Financial Portfolio Management System

A DBMS-based project designed to efficiently manage and track financial investments including stocks, bonds, mutual funds, and real estate assets.

🚀 Project Overview

The Financial Portfolio Management System is a relational database project developed using MySQL and SQL to help users organize, monitor, and analyze their investment portfolios efficiently.

This project demonstrates the practical implementation of important Database Management System (DBMS) concepts such as:

✅ ER Modeling
✅ Relational Database Design
✅ Normalization (up to 3NF)
✅ SQL Queries
✅ Joins & Subqueries
✅ Aggregate Functions
✅ Views
✅ Referential Integrity using PK & FK

The system enables users to manage investments, track transactions, analyze risk, and maintain historical asset price records in a structured database environment.

🎯 Objectives

✔️ Manage user investment portfolios efficiently
✔️ Track multiple financial assets
✔️ Maintain transaction records
✔️ Analyze investment risk levels
✔️ Store historical asset prices
✔️ Generate portfolio performance reports

🛠️ Technology Stack
Technology	Purpose
🗄️ MySQL	Database Management
💻 SQL	Querying & Data Manipulation
📐 ER Modeling	Database Design
📊 Views & Queries	Reporting & Analysis
🐍 Python (Future Scope)	Financial Analytics & Visualization
✨ Key Features

📌 Portfolio Tracking
📌 Asset Management
📌 Transaction Recording
📌 Risk Analysis
📌 Historical Price Tracking
📌 Reporting using SQL Views
📌 Relational Database Design

🧩 Database Entities

The project consists of the following entities:

Entity	Description
👤 USERS	Stores investor details
💼 PORTFOLIO	Stores user investment holdings
📈 ASSETS	Stores asset information
🗂️ ASSET_CATEGORIES	Classifies asset types
⚠️ RISK_PROFILES	Stores investment risk levels
🏦 BROKERS	Stores broker details
💳 TRANSACTIONS	Records buy/sell operations
📊 ASSET_PRICES	Stores historical asset prices
🔗 ER Diagram

The ER Diagram represents the relationships among:

👤 Users
💼 Portfolios
📈 Assets
💳 Transactions
🏦 Brokers
⚠️ Risk Profiles
📊 Historical Asset Prices
Main Relationships

✔️ One user can have multiple portfolio records
✔️ One portfolio can contain multiple transactions
✔️ One asset belongs to one category
✔️ One asset can have multiple historical price records
✔️ Transactions are associated with brokers

🧠 Normalization

The database schema is normalized up to Third Normal Form (3NF) to reduce redundancy and improve data consistency.

✅ First Normal Form (1NF)
Atomic values are maintained
No repeating groups
✅ Second Normal Form (2NF)
Full dependency on primary keys
No partial dependency
✅ Third Normal Form (3NF)
No transitive dependency
Separate tables created for:
🏦 Brokers
🗂️ Asset Categories
⚠️ Risk Profiles
🧮 SQL Concepts Used
🔗 Joins

Used to combine related data from multiple tables.

📊 Aggregate Functions

Used for calculations such as:

SUM()
AVG()
COUNT()
🪄 Subqueries

Used for nested filtering and analysis.

👁️ Views

Used to simplify complex reporting queries.

Example Views
portfolio_summary_view
asset_risk_view
🔑 Primary Keys & Foreign Keys
✅ Primary Keys

Each table contains a unique primary key:

user_id
portfolio_id
asset_id
transaction_id
broker_id
category_id
risk_id
price_id
🔄 Foreign Keys

Foreign keys maintain relationships among tables and ensure referential integrity.

Examples
user_id in PORTFOLIO references USERS
asset_id in PORTFOLIO references ASSETS
broker_id in TRANSACTIONS references BROKERS
📌 Sample Functionalities

✔️ Add and manage investors
✔️ Track asset holdings
✔️ Record transactions
✔️ Analyze investment risk
✔️ Monitor historical asset performance
✔️ Generate portfolio reports

📈 Future Enhancements

🚀 Real-time stock market integration
📊 Dashboard analytics
📱 Web & Mobile Application
🤖 Automated Reporting
🐍 Python-based Financial Analysis
⚡ Stored Procedures & Triggers

✅ Conclusion

The Financial Portfolio Management System demonstrates how DBMS concepts can be applied to efficiently manage financial investment data using relational database techniques.

The project successfully provides:

✔️ Structured Data Management
✔️ Reduced Redundancy
✔️ Efficient Reporting
✔️ Portfolio Tracking
✔️ Risk Analysis
✔️ Historical Data Maintenance

👩‍💻 Developed By
Manasa Konala

🎓 B.Tech – Computer Science and Engineering
🏫 SRM University-AP
