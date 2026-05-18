from __future__ import annotations

from decimal import Decimal
from io import StringIO
from typing import Any
import csv

from flask import (
    Flask,
    Response,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
import mysql.connector
from mysql.connector import pooling

app = Flask(__name__)
app.secret_key = "change-this-secret-key"

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Manasakonala@15",
    "database": "wealth_portfolio_management",
}

connection_pool = pooling.MySQLConnectionPool(
    pool_name="portfolio_pool",
    pool_size=5,
    **DB_CONFIG,
)


def get_connection():
    return connection_pool.get_connection()


def fetch_all(query: str, params: tuple = ()) -> list[dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def fetch_one(query: str, params: tuple = ()) -> dict[str, Any] | None:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params)
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def execute_query(query: str, params: tuple = ()) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    cursor.close()
    conn.close()


def login_required() -> bool:
    return "user_id" in session


@app.template_filter("money")
def money_filter(value: Any) -> str:
    if value is None:
        return "₹0.00"
    if isinstance(value, Decimal):
        value = float(value)
    return f"₹{value:,.2f}"


@app.context_processor
def inject_sidebar_state():
    return {"active_page": request.endpoint}


@app.route("/")
def home():
    if login_required():
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip()
        password = request.form["password"].strip()

        existing = fetch_one("SELECT user_id FROM users WHERE email = %s", (email,))
        if existing:
            flash("Email already exists. Please log in.", "warning")
            return redirect(url_for("login"))

        execute_query(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
            (name, email, password),
        )
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html", title="Register")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip()
        password = request.form["password"].strip()

        user = fetch_one(
            "SELECT user_id, name, email FROM users WHERE email = %s AND password = %s",
            (email, password),
        )

        if user:
            session["user_id"] = user["user_id"]
            session["user_name"] = user["name"]
            flash("Login successful.", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid email or password.", "danger")

    return render_template("login.html", title="Login")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


def get_summary(user_id: int) -> dict[str, Any] | None:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.callproc("GetPortfolioSummary", [user_id])
    summary = None
    for result in cursor.stored_results():
        summary = result.fetchone()
    cursor.close()
    conn.close()
    return summary


def get_assets() -> list[dict[str, Any]]:
    return fetch_all(
        """
        SELECT a.asset_id, a.asset_name, c.category_name
        FROM assets a
        JOIN asset_categories c ON a.category_id = c.category_id
        ORDER BY a.asset_name
        """
    )


@app.route("/dashboard")
def dashboard():
    if not login_required():
        return redirect(url_for("login"))

    user_id = session["user_id"]
    summary = get_summary(user_id)

    holdings = fetch_all(
        """
        SELECT *
        FROM portfolio_summary_view
        WHERE user_id = %s
        ORDER BY current_value DESC
        LIMIT 5
        """,
        (user_id,),
    )

    allocation = fetch_all(
        """
        SELECT category_name, SUM(current_value) AS total_value
        FROM portfolio_summary_view
        WHERE user_id = %s
        GROUP BY category_name
        ORDER BY total_value DESC
        """,
        (user_id,),
    )

    recent_transactions = fetch_all(
        """
        SELECT t.transaction_id, a.asset_name, t.transaction_type, t.quantity, t.price, t.transaction_date
        FROM transactions t
        JOIN portfolio p ON t.portfolio_id = p.portfolio_id
        JOIN assets a ON p.asset_id = a.asset_id
        WHERE p.user_id = %s
        ORDER BY t.transaction_date DESC, t.transaction_id DESC
        LIMIT 5
        """,
        (user_id,),
    )

    return render_template(
        "dashboard.html",
        title="Dashboard",
        summary=summary,
        holdings=holdings,
        allocation=allocation,
        recent_transactions=recent_transactions,
    )


@app.route("/holdings")
def holdings():
    if not login_required():
        return redirect(url_for("login"))

    user_id = session["user_id"]
    summary = get_summary(user_id)
    holdings_data = fetch_all(
        """
        SELECT *
        FROM portfolio_summary_view
        WHERE user_id = %s
        ORDER BY current_value DESC
        """,
        (user_id,),
    )
    assets = get_assets()
    return render_template(
        "holdings.html",
        title="Holdings",
        summary=summary,
        holdings=holdings_data,
        assets=assets,
    )


@app.route("/transactions")
def transactions():
    if not login_required():
        return redirect(url_for("login"))

    txns = fetch_all(
        """
        SELECT t.transaction_id, a.asset_name, t.transaction_type, t.quantity, t.price,
               (t.quantity * t.price) AS trade_value, t.transaction_date,
               COALESCE(b.broker_name, 'Direct') AS broker_name
        FROM transactions t
        JOIN portfolio p ON t.portfolio_id = p.portfolio_id
        JOIN assets a ON p.asset_id = a.asset_id
        LEFT JOIN brokers b ON t.broker_id = b.broker_id
        WHERE p.user_id = %s
        ORDER BY t.transaction_date DESC, t.transaction_id DESC
        """,
        (session["user_id"],),
    )
    return render_template("transactions.html", title="Transactions", transactions=txns)


@app.route("/analytics")
def analytics():
    if not login_required():
        return redirect(url_for("login"))

    user_id = session["user_id"]

    risk_data = fetch_all(
        """
        SELECT risk_level, COUNT(*) AS total_assets
        FROM portfolio_summary_view
        WHERE user_id = %s
        GROUP BY risk_level
        ORDER BY FIELD(risk_level, 'Low', 'Medium', 'High')
        """,
        (user_id,),
    )

    trend_data = fetch_all(
        """
        SELECT t.transaction_date, SUM(t.price * t.quantity) AS total_value
        FROM transactions t
        JOIN portfolio p ON t.portfolio_id = p.portfolio_id
        WHERE p.user_id = %s
        GROUP BY t.transaction_date
        ORDER BY t.transaction_date
        """,
        (user_id,),
    )

    asset_performance = fetch_all(
        """
        SELECT asset_name, profit, return_percent, current_value
        FROM portfolio_summary_view
        WHERE user_id = %s
        ORDER BY current_value DESC
        """,
        (user_id,),
    )

    trend_labels = [row["transaction_date"].strftime("%Y-%m-%d") if hasattr(row["transaction_date"], "strftime") else str(row["transaction_date"]) for row in trend_data]
    trend_values = [float(row["total_value"] or 0) for row in trend_data]
    risk_labels = [row["risk_level"] for row in risk_data]
    risk_values = [int(row["total_assets"] or 0) for row in risk_data]

    return render_template(
        "analytics.html",
        title="Analytics",
        risk_data=risk_data,
        trend_data=trend_data,
        asset_performance=asset_performance,
        trend_labels=trend_labels,
        trend_values=trend_values,
        risk_labels=risk_labels,
        risk_values=risk_values,
    )


@app.route("/add-holding", methods=["POST"])
def add_holding():
    if not login_required():
        return redirect(url_for("login"))

    user_id = session["user_id"]
    asset_id = request.form["asset_id"]
    quantity = request.form["quantity"]
    buy_price = request.form["buy_price"]
    buy_date = request.form["buy_date"]

    execute_query(
        """
        INSERT INTO portfolio (user_id, asset_id, quantity, buy_price, buy_date)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (user_id, asset_id, quantity, buy_price, buy_date),
    )
    flash("Holding added successfully. BUY transaction created automatically.", "success")
    return redirect(url_for("holdings"))


@app.route("/add-price", methods=["POST"])
def add_price():
    if not login_required():
        return redirect(url_for("login"))

    asset_id = request.form["asset_id"]
    price = request.form["price"]
    price_date = request.form["price_date"]

    execute_query(
        "INSERT INTO asset_prices (asset_id, price, price_date) VALUES (%s, %s, %s)",
        (asset_id, price, price_date),
    )
    flash("Price history added successfully.", "success")
    return redirect(url_for("holdings"))


@app.route("/report")
def report():
    if not login_required():
        return redirect(url_for("login"))

    user_id = session["user_id"]
    summary = get_summary(user_id)
    performance = fetch_all(
        """
        SELECT asset_name, category_name, risk_level, investment, current_value, profit, return_percent
        FROM portfolio_summary_view
        WHERE user_id = %s
        ORDER BY current_value DESC
        """,
        (user_id,),
    )
    return render_template(
        "report.html",
        title="Report",
        summary=summary,
        performance=performance,
    )


@app.route("/download-report")
def download_report():
    if not login_required():
        return redirect(url_for("login"))

    user_id = session["user_id"]
    rows = fetch_all(
        """
        SELECT asset_name, category_name, risk_level, quantity, buy_price, current_price,
               investment, current_value, profit, return_percent
        FROM portfolio_summary_view
        WHERE user_id = %s
        ORDER BY current_value DESC
        """,
        (user_id,),
    )
    summary = get_summary(user_id) or {}

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Financial Portfolio Report"])
    writer.writerow(["User", session.get("user_name", "")])
    writer.writerow([])
    writer.writerow(["Total Investment", summary.get("total_investment", 0)])
    writer.writerow(["Current Value", summary.get("current_value", 0)])
    writer.writerow(["Total Profit", summary.get("total_profit", 0)])
    writer.writerow(["Return Percentage", summary.get("return_percentage", 0)])
    writer.writerow([])
    writer.writerow(
        [
            "Asset",
            "Category",
            "Risk",
            "Quantity",
            "Buy Price",
            "Current Price",
            "Investment",
            "Current Value",
            "Profit",
            "Return %",
        ]
    )
    for row in rows:
        writer.writerow(
            [
                row["asset_name"],
                row["category_name"],
                row["risk_level"],
                row["quantity"],
                row["buy_price"],
                row["current_price"],
                row["investment"],
                row["current_value"],
                row["profit"],
                row["return_percent"],
            ]
        )

    csv_data = output.getvalue()
    output.close()

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=portfolio_report.csv"
        },
    )


if __name__ == "__main__":
    app.run(debug=True)
