# Auto-generated schemas for category: banking

import pandas as pd
import pandera as pa
from pandera.typing import Series, String, Int, Float, Bool, DateTime
import pandera.extensions as extensions
from brynq_sdk_functions import BrynQPanderaDataFrameModel
from typing import Optional, Annotated
from pydantic import BaseModel, Field, StringConstraints

class Bank_accountsGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Factorial unique identifier.", alias="id")
    external_id: Series[String] = pa.Field(coerce=True, nullable=False, description="External ID for the bank account.", alias="external_id")
    currency: Series[String] = pa.Field(coerce=True, nullable=False, description="Currency.", alias="currency")
    country: Series[String] = pa.Field(coerce=True, nullable=False, description="Country.", alias="country")
    account_number: Series[String] = pa.Field(coerce=True, nullable=False, description="Account number.", alias="account_number")
    account_number_type: Series[String] = pa.Field(coerce=True, nullable=False, description="Account number type.", alias="account_number_type")
    sort_code: Series[String] = pa.Field(coerce=True, nullable=True, description="Sort code.", alias="sort_code")
    bic: Series[String] = pa.Field(coerce=True, nullable=True, description="Bank Identifier Code.", alias="bic")
    iban: Series[String] = pa.Field(coerce=True, nullable=True, description="International Bank Account Number.", alias="iban")
    routing_number: Series[String] = pa.Field(coerce=True, nullable=True, description="Routing number.", alias="routing_number")
    account_balance_cents: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Account balance in cents.", alias="account_balance_cents")
    available_balance_cents: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Available balance in cents.", alias="available_balance_cents")
    pending_balance_cents: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Pending balance in cents.", alias="pending_balance_cents")
    beneficiary_name: Series[String] = pa.Field(coerce=True, nullable=True, description="Beneficiary name.", alias="beneficiary_name")
    bank_name: Series[String] = pa.Field(coerce=True, nullable=True, description="Bank name.", alias="bank_name")
    account_alias: Series[String] = pa.Field(coerce=True, nullable=True, description="Account alias.", alias="account_alias")
    updated_at: Series[String] = pa.Field(coerce=True, nullable=False, description="Last updated date.", alias="updated_at")
    legal_entity_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="Factorial unique identifier of the legal entity.", alias="legal_entity_id")

    class _Annotation:
        primary_key = "id"
        foreign_keys = {
            "legal_entity_id": {
                "parent_schema": "Legal_entitiesGet",
                "parent_column": "id",
                "cardinality": "N:1"
            }
        }

class TransactionsGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Factorial unique identifier.", alias="id")
    bank_account_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Factorial Banking Bank Account unique identifier.", alias="bank_account_id")
    amount_cents: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Amount in cents.", alias="amount_cents")
    balance_after_cents: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="Balance after the transaction in cents.", alias="balance_after_cents")
    currency: Series[String] = pa.Field(coerce=True, nullable=False, description="Currency.", alias="currency")
    type: Series[String] = pa.Field(coerce=True, nullable=False, description="Type of transaction.", alias="type")
    description: Series[String] = pa.Field(coerce=True, nullable=True, description="Description of the transaction.", alias="description")
    booking_date: Series[String] = pa.Field(coerce=True, nullable=False, description="Booking date of the transaction.", alias="booking_date")
    value_date: Series[String] = pa.Field(coerce=True, nullable=False, description="Value date of the transaction.", alias="value_date")
    updated_at: Series[String] = pa.Field(coerce=True, nullable=False, description="Date when the transaction was last updated.", alias="updated_at")

    class _Annotation:
        primary_key = "id"
        foreign_keys = {
            "bank_account_id": {
                "parent_schema": "Bank_accountsGet",
                "parent_column": "id",
                "cardinality": "N:1"
            }
        }

class Bank_accountsCreate(BaseModel):
    id: int = Field(..., description="Factorial unique identifier.", alias="id")
    external_id: str = Field(..., description="External ID for the bank account.", alias="external_id")
    currency: str = Field(..., description="Currency.", alias="currency")
    country: str = Field(..., description="Country.", alias="country")
    account_number: str = Field(..., description="Account number.", alias="account_number")
    account_number_type: Annotated[str, StringConstraints(pattern=r'^iban|sort_code_and_account_number|routing_number_and_account_number|clabe|other|bank_name_and_account_number$', strip_whitespace=True)] = Field(..., description="Account number type.", alias="account_number_type")
    sort_code: Optional[str] = Field(None, description="Sort code.", alias="sort_code")
    bic: Optional[str] = Field(None, description="Bank Identifier Code.", alias="bic")
    iban: Optional[str] = Field(None, description="International Bank Account Number.", alias="iban")
    routing_number: Optional[str] = Field(None, description="Routing number.", alias="routing_number")
    account_balance_cents: int = Field(..., description="Account balance in cents.", alias="account_balance_cents")
    available_balance_cents: int = Field(..., description="Available balance in cents.", alias="available_balance_cents")
    pending_balance_cents: int = Field(..., description="Pending balance in cents.", alias="pending_balance_cents")
    beneficiary_name: Optional[str] = Field(None, description="Beneficiary name.", alias="beneficiary_name")
    bank_name: Optional[str] = Field(None, description="Bank name.", alias="bank_name")
    account_alias: Optional[str] = Field(None, description="Account alias.", alias="account_alias")
    updated_at: str = Field(..., description="Last updated date.", alias="updated_at")
    legal_entity_id: Optional[int] = Field(None, description="Factorial unique identifier of the legal entity.", alias="legal_entity_id")

class Bank_accountsDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

class TransactionsDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")
