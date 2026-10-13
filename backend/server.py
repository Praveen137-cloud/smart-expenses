"""FastAPI application: REST API + static frontend."""
import logging
from contextlib import asynccontextmanager
from datetime import date
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func, text
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from backend import config, ml_classifier
from backend.database import Base, SessionLocal, engine, get_db
from backend.models import Budget, Category, Transaction
from backend.schemas import BudgetPayload, CategorizeRequest, TransactionPayload
from backend.seed_data import seed_database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("expense_tracker")
USER_ID = config.DEFAULT_USER_ID


@asynccontextmanager
async def lifespan(app: FastAPI):
    ml_classifier.load_model()  # trains automatically when the model file is missing
    try:
        Base.metadata.create_all(bind=engine)
        with SessionLocal() as db_session:
            seed_database(db_session)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection OK.")
    except SQLAlchemyError as exc:
        logger.warning("Database error: %s", exc)
    yield


app = FastAPI(title="Smart Expense & Personal Finance Tracker", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------- error handling
@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    errors = [
        {"field": ".".join(str(p) for p in e["loc"] if p not in ("body", "query")), "message": e["msg"]}
        for e in exc.errors()
    ]
    detail = "; ".join(f'{e["field"]}: {e["message"]}' if e["field"] else e["message"] for e in errors)
    return JSONResponse(status_code=422, content={"success": False, "detail": detail or "Invalid request", "errors": errors})


@app.exception_handler(OperationalError)
async def db_unavailable_handler(request: Request, exc: OperationalError):
    logger.error("Database error: %s", exc)
    return JSONResponse(status_code=503, content={
        "success": False,
        "detail": "Cannot reach the database. Make sure MySQL is running, finance_db exists and .env is correct.",
    })


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
    logger.error("Database error: %s", exc)
    return JSONResponse(status_code=500, content={"success": False, "detail": "A database error occurred."})


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error")
    return JSONResponse(status_code=500, content={"success": False, "detail": "Internal server error."})


# ---------------------------------------------------------------- helpers
def month_bounds(month: Optional[int], year: Optional[int]) -> tuple[date, date]:
    """Return [start, end) dates for a month, defaulting to the current month."""
    today = date.today()
    month, year = month or today.month, year or today.year
    start = date(year, month, 1)
    end = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)
    return start, end


def tx_out(t: Transaction) -> dict:
    return {
        "id": t.id,
        "category_id": t.category_id,
        "category": t.category.name if t.category else None,
        "description": t.description,
        "amount": float(t.amount),
        "transaction_date": t.transaction_date.isoformat(),
        "payment_method": t.payment_method,
        "predicted_category": t.predicted_category,
        "prediction_confidence": float(t.prediction_confidence) if t.prediction_confidence is not None else None,
        "notes": t.notes,
        "created_at": t.created_at.isoformat() if t.created_at else None,
    }


def budget_out(b: Budget) -> dict:
    return {
        "id": b.id, "category_id": b.category_id, "category": b.category.name if b.category else None,
        "month": b.month, "year": b.year, "budget_amount": float(b.budget_amount),
    }


def require_category(db: Session, category_id: int) -> Category:
    category = db.get(Category, category_id)
    if category is None:
        raise HTTPException(status_code=400, detail="Invalid category ID.")
    return category


def category_totals(db: Session, start: date, end: date):
    total = func.sum(Transaction.amount)
    return (
        db.query(Category.id, Category.name, total)
        .join(Transaction, Transaction.category_id == Category.id)
        .filter(Transaction.user_id == USER_ID, Transaction.transaction_date >= start, Transaction.transaction_date < end)
        .group_by(Category.id, Category.name)
        .order_by(total.desc())
        .all()
    )


def budget_status(percentage: float) -> str:
    if percentage >= 100:
        return "exceeded"
    return "warning" if percentage >= 80 else "safe"


def ensure_unique_budget(db: Session, payload: BudgetPayload, exclude_id: Optional[int] = None) -> None:
    query = db.query(Budget).filter(
        Budget.user_id == USER_ID, Budget.category_id == payload.category_id,
        Budget.month == payload.month, Budget.year == payload.year,
    )
    if exclude_id is not None:
        query = query.filter(Budget.id != exclude_id)
    if query.first():
        raise HTTPException(status_code=409, detail="A budget for this category, month and year already exists.")


# ---------------------------------------------------------------- health & categories
@app.get("/api/v1/health")
def health():
    return {"status": "ok"}


@app.get("/api/v1/categories")
def list_categories(db: Session = Depends(get_db)):
    return [{"id": c.id, "name": c.name, "description": c.description}
            for c in db.query(Category).order_by(Category.id).all()]


# ---------------------------------------------------------------- transactions
@app.post("/api/v1/transactions/categorize")
def categorize(payload: CategorizeRequest):
    result = ml_classifier.predict_category(payload.description)
    return {
        "success": True,
        "description": payload.description,
        "predicted_category": result["category"],
        "confidence": result["confidence"],
        "low_confidence": result["low_confidence"],
    }


@app.get("/api/v1/transactions")
def list_transactions(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000, le=2100),
    category_id: Optional[int] = None,
    search: Optional[str] = Query(None, max_length=100),
    on_date: Optional[date] = Query(None, alias="date"),
    min_amount: Optional[float] = Query(None, ge=0),
    max_amount: Optional[float] = Query(None, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(Transaction).options(joinedload(Transaction.category)).filter(Transaction.user_id == USER_ID)
    if month or year:
        start, end = month_bounds(month, year) if month else (date(year, 1, 1), date(year + 1, 1, 1))
        query = query.filter(Transaction.transaction_date >= start, Transaction.transaction_date < end)
    if category_id:
        query = query.filter(Transaction.category_id == category_id)
    if search:
        query = query.filter(Transaction.description.ilike(f"%{search.strip()}%"))
    if on_date:
        query = query.filter(Transaction.transaction_date == on_date)
    if min_amount is not None:
        query = query.filter(Transaction.amount >= min_amount)
    if max_amount is not None:
        query = query.filter(Transaction.amount <= max_amount)
    rows = query.order_by(Transaction.transaction_date.desc(), Transaction.id.desc()).all()
    return [tx_out(t) for t in rows]


@app.post("/api/v1/transactions", status_code=201)
def create_transaction(payload: TransactionPayload, db: Session = Depends(get_db)):
    require_category(db, payload.category_id)
    tx = Transaction(user_id=USER_ID, **payload.model_dump())
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx_out(tx)


@app.get("/api/v1/transactions/{tx_id}")
def get_transaction(tx_id: int, db: Session = Depends(get_db)):
    tx = db.query(Transaction).options(joinedload(Transaction.category)).filter(
        Transaction.id == tx_id, Transaction.user_id == USER_ID).first()
    if tx is None:
        raise HTTPException(status_code=404, detail="Transaction not found.")
    return tx_out(tx)


@app.put("/api/v1/transactions/{tx_id}")
def update_transaction(tx_id: int, payload: TransactionPayload, db: Session = Depends(get_db)):
    tx = db.query(Transaction).filter(Transaction.id == tx_id, Transaction.user_id == USER_ID).first()
    if tx is None:
        raise HTTPException(status_code=404, detail="Transaction not found.")
    require_category(db, payload.category_id)
    for field, value in payload.model_dump().items():
        setattr(tx, field, value)
    db.commit()
    db.refresh(tx)
    return tx_out(tx)


@app.delete("/api/v1/transactions/{tx_id}")
def delete_transaction(tx_id: int, db: Session = Depends(get_db)):
    tx = db.query(Transaction).filter(Transaction.id == tx_id, Transaction.user_id == USER_ID).first()
    if tx is None:
        raise HTTPException(status_code=404, detail="Transaction not found.")
    db.delete(tx)
    db.commit()
    return {"success": True}


# ---------------------------------------------------------------- budgets
@app.get("/api/v1/budgets")
def list_budgets(month: Optional[int] = Query(None, ge=1, le=12), year: Optional[int] = Query(None, ge=2000, le=2100),
                 db: Session = Depends(get_db)):
    query = db.query(Budget).options(joinedload(Budget.category)).filter(Budget.user_id == USER_ID)
    if month:
        query = query.filter(Budget.month == month)
    if year:
        query = query.filter(Budget.year == year)
    return [budget_out(b) for b in query.order_by(Budget.year.desc(), Budget.month.desc(), Budget.category_id).all()]


@app.post("/api/v1/budgets", status_code=201)
def create_budget(payload: BudgetPayload, db: Session = Depends(get_db)):
    require_category(db, payload.category_id)
    ensure_unique_budget(db, payload)
    budget = Budget(user_id=USER_ID, **payload.model_dump())
    db.add(budget)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="A budget for this category, month and year already exists.")
    db.refresh(budget)
    return budget_out(budget)


@app.put("/api/v1/budgets/{budget_id}")
def update_budget(budget_id: int, payload: BudgetPayload, db: Session = Depends(get_db)):
    budget = db.query(Budget).filter(Budget.id == budget_id, Budget.user_id == USER_ID).first()
    if budget is None:
        raise HTTPException(status_code=404, detail="Budget not found.")
    require_category(db, payload.category_id)
    ensure_unique_budget(db, payload, exclude_id=budget_id)
    for field, value in payload.model_dump().items():
        setattr(budget, field, value)
    db.commit()
    db.refresh(budget)
    return budget_out(budget)


@app.delete("/api/v1/budgets/{budget_id}")
def delete_budget(budget_id: int, db: Session = Depends(get_db)):
    budget = db.query(Budget).filter(Budget.id == budget_id, Budget.user_id == USER_ID).first()
    if budget is None:
        raise HTTPException(status_code=404, detail="Budget not found.")
    db.delete(budget)
    db.commit()
    return {"success": True}


# ---------------------------------------------------------------- dashboard
@app.get("/api/v1/dashboard/summary")
def dashboard_summary(month: Optional[int] = Query(None, ge=1, le=12), year: Optional[int] = Query(None, ge=2000, le=2100),
                      db: Session = Depends(get_db)):
    start, end = month_bounds(month, year)
    total, count = db.query(func.coalesce(func.sum(Transaction.amount), 0), func.count(Transaction.id)).filter(
        Transaction.user_id == USER_ID, Transaction.transaction_date >= start, Transaction.transaction_date < end).one()
    totals = category_totals(db, start, end)
    budget_total = db.query(func.coalesce(func.sum(Budget.budget_amount), 0)).filter(
        Budget.user_id == USER_ID, Budget.month == start.month, Budget.year == start.year).scalar()
    return {
        "month": start.month,
        "year": start.year,
        "total_spending": float(total),
        "transaction_count": int(count),
        "highest_category": totals[0][1] if totals else None,
        "highest_category_amount": float(totals[0][2]) if totals else 0,
        "monthly_budget": float(budget_total),
        "remaining_budget": float(budget_total) - float(total),
    }


@app.get("/api/v1/dashboard/category-spending")
def dashboard_category_spending(month: Optional[int] = Query(None, ge=1, le=12),
                                year: Optional[int] = Query(None, ge=2000, le=2100), db: Session = Depends(get_db)):
    start, end = month_bounds(month, year)
    return [{"category": name, "amount": float(amount)} for _, name, amount in category_totals(db, start, end)]


@app.get("/api/v1/dashboard/budget-comparison")
def dashboard_budget_comparison(month: Optional[int] = Query(None, ge=1, le=12),
                                year: Optional[int] = Query(None, ge=2000, le=2100), db: Session = Depends(get_db)):
    start, end = month_bounds(month, year)
    actuals = {cid: float(amount) for cid, _, amount in category_totals(db, start, end)}
    budgets = (db.query(Budget).options(joinedload(Budget.category))
               .filter(Budget.user_id == USER_ID, Budget.month == start.month, Budget.year == start.year)
               .order_by(Budget.category_id).all())
    result = []
    for b in budgets:
        budget_amount = float(b.budget_amount)
        actual = actuals.get(b.category_id, 0.0)
        percentage = round(actual / budget_amount * 100, 2) if budget_amount else 0.0
        result.append({
            "budget_id": b.id, "category_id": b.category_id, "category": b.category.name,
            "month": b.month, "year": b.year, "budget": budget_amount, "actual": actual,
            "remaining": round(budget_amount - actual, 2), "percentage_used": percentage,
            "status": budget_status(percentage),
        })
    return result


# ---------------------------------------------------------------- frontend
app.mount("/static", StaticFiles(directory=config.FRONTEND_DIR), name="static")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(config.FRONTEND_DIR / "index.html")
