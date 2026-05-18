# Financial Portfolio Management System

## 1. Create the database
Run this in MySQL:

```sql
SOURCE schema.sql;
```

Or open the file and run the whole script in MySQL Workbench.

## 2. Install packages
```bash
pip install -r requirements.txt
```

If `pip` does not work on your Mac, use:
```bash
python3 -m pip install -r requirements.txt
```

## 3. Update database password
Open `app.py` and change:
```python
"password": "YOUR_MYSQL_PASSWORD"
```

## 4. Run the Flask app
```bash
python app.py
```

If that does not work on Mac, use:
```bash
python3 app.py
```

## 5. Open in browser
```text
http://127.0.0.1:5000
```

## Demo login from sample data
- Email: `manasa@gmail.com`
- Password: `1234`

## What this app includes
- User registration and login
- Portfolio dashboard
- Holdings table
- Add new holding
- Add price history
- Profit and return summary
- Risk chart
- Trend chart
- Performance report
