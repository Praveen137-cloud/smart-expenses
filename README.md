# Smart Expense & Personal Finance Tracker

A full-stack personal finance app: record expenses, let a machine-learning model suggest the category, set monthly budgets, and watch budget alerts and charts update on a dashboard.

## 1. Overview
```
Browser (HTML/CSS/JS + Chart.js) --fetch/JSON--> FastAPI --> MySQL (finance_db)
                                                    |-----> scikit-learn classifier
                                                    |-----> budget / alert logic
```
FastAPI also serves the frontend, so only one server runs.

## 2. Features
- Add / edit / delete expenses; search and filter by text, category, date and amount
- AI category suggestion with confidence; accept it or override it (your choice is what gets saved)
- Monthly budgets per category (unique per category + month + year)
- Dashboard: summary cards, spending doughnut chart, budget-vs-actual bar chart, progress bars
- In-page alerts and toasts (80% = warning, 100%+ = exceeded)
- Swagger docs at `/docs`

## 3. Tech stack
HTML5, CSS3, vanilla JavaScript, Chart.js | Python 3.11+, FastAPI, Uvicorn, Pydantic, SQLAlchemy, PyMySQL | MySQL 8+ | scikit-learn (CountVectorizer + MultinomialNB), joblib

## 4. Folder structure
```
smart-expense-tracker/
  backend/   server.py database.py models.py schemas.py config.py
             ml_classifier.py train_classifier.py requirements.txt model/
  frontend/  index.html dashboard.js styles.css
  database/  finance_db.sql
  .env.example  .gitignore  setup.bat  start.bat  README.md
```

## 5. Requirements
- Windows 10/11, Python 3.11+ (added to PATH), MySQL 8+, internet on first run (pip packages; Chart.js loads from a CDN)

## 6-8. MySQL, database and .env
1. Install MySQL 8+ (MySQL Installer for Windows) and remember the root password.
2. Open MySQL Workbench (or the MySQL command line).
3. Run `SOURCE database/finance_db.sql;` (Workbench: *File > Run SQL Script...*). This creates `finance_db`, the tables and sample data. Re-running it resets the data.
4. Copy `.env.example` to `.env` (the batch files do this for you).
5. Edit `.env`: set `DB_USER` and `DB_PASSWORD`.

## 9-12. First-time setup and running
- **First time:** double-click `setup.bat` (venv, dependencies, `.env`, model training).
- **Every time after:** double-click `start.bat`. It opens http://127.0.0.1:8000 automatically.
- Swagger: http://127.0.0.1:8000/docs

## 14. Train the model manually
```
.venv\Scripts\activate
python backend\train_classifier.py
```
The model is saved to `backend/model/expense_classifier.pkl`. If it is missing, the server trains it automatically at startup. Descriptions with no known words, or confidence below 45%, are returned as **Other** with a low-confidence flag.

## 15. API endpoints (prefix `/api/v1`)
| Method | Path | Purpose |
|---|---|---|
| GET | /health | Health check |
| GET | /categories | List categories |
| POST | /transactions/categorize | ML category prediction |
| GET | /transactions | List (`month, year, category_id, search, date, min_amount, max_amount`) |
| POST | /transactions | Create |
| GET / PUT / DELETE | /transactions/{id} | Read / update / delete |
| GET / POST | /budgets | List (`month, year`) / create |
| PUT / DELETE | /budgets/{id} | Update / delete |
| GET | /dashboard/summary | Totals for a month (`month, year`, default current) |
| GET | /dashboard/category-spending | Spend per category |
| GET | /dashboard/budget-comparison | Budget vs actual + status |

## 16. Troubleshooting
| Problem | Fix |
|---|---|
| "Python was not found" | Reinstall Python and tick *Add to PATH* |
| "Cannot reach the database" | Start the MySQL service; check `.env`; import `finance_db.sql` |
| `Access denied for user` | Wrong `DB_USER` / `DB_PASSWORD` in `.env` |
| `Unknown database 'finance_db'` | Run `database/finance_db.sql` |
| Dependencies fail to install | Check internet; delete `.venv` and run `setup.bat` again |
| Charts are blank | Chart.js loads from the internet; check your connection |
| Port 8000 busy | Close the other program or change the port in `start.bat` |
| Dashboard looks empty | Sample data is for October 2026 - pick that month, or add expenses |
