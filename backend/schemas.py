"""Pydantic request schemas with validation."""
from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, field_validator

PAYMENT_METHODS = ["Cash", "UPI", "Credit Card", "Debit Card", "Net Banking", "Other"]


def _clean_text(value: str, label: str) -> str:
    value = (value or "").strip()
    if not value:
        raise ValueError(f"{label} must not be empty")
    return value


class CategorizeRequest(BaseModel):
    description: str = Field(..., max_length=255)

    @field_validator("description")
    @classmethod
    def description_not_blank(cls, v: str) -> str:
        return _clean_text(v, "Description")


class TransactionPayload(BaseModel):
    description: str = Field(..., max_length=255)
    amount: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)
    transaction_date: date
    payment_method: str = "Cash"
    category_id: int = Field(..., gt=0)
    notes: Optional[str] = Field(None, max_length=1000)
    predicted_category: Optional[str] = Field(None, max_length=50)
    prediction_confidence: Optional[float] = Field(None, ge=0, le=1)

    @field_validator("description")
    @classmethod
    def description_not_blank(cls, v: str) -> str:
        return _clean_text(v, "Description")

    @field_validator("payment_method")
    @classmethod
    def valid_payment_method(cls, v: str) -> str:
        if v not in PAYMENT_METHODS:
            raise ValueError("Payment method must be one of: " + ", ".join(PAYMENT_METHODS))
        return v


class BudgetPayload(BaseModel):
    category_id: int = Field(..., gt=0)
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2000, le=2100)
    budget_amount: Decimal = Field(..., gt=0, max_digits=10, decimal_places=2)
