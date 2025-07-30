# Auto-generated schemas for category: payroll

import pandas as pd
import pandera as pa
from pandera.typing import Series, String, Int, Float, Bool, DateTime
import pandera.extensions as extensions
from brynq_sdk_functions import BrynQPanderaDataFrameModel
from typing import Optional, Annotated
from pydantic import BaseModel, Field, StringConstraints

class SupplementsGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="The identifier of the supplement", alias="id")
    employee_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="The identifier of the employee associated with the supplement", alias="employee_id")
    company_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="The identifier of the company associated with the supplement", alias="company_id")
    contracts_compensation_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="The contract compensation identifier associated with the supplement", alias="contracts_compensation_id")
    contracts_taxonomy_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="The taxonomy identifier associated with the supplement", alias="contracts_taxonomy_id")
    amount_in_cents: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="The amount of the supplement in cents", alias="amount_in_cents")
    unit: Series[String] = pa.Field(coerce=True, nullable=False, description="The unit of the supplement", alias="unit")
    effective_on: Series[String] = pa.Field(coerce=True, nullable=True, description="The date on which the supplement becomes effective", alias="effective_on")
    created_at: Series[Bool] = pa.Field(coerce=True, nullable=True, description="The created at date when the supplement was created", alias="created_at")
    updated_at: Series[Bool] = pa.Field(coerce=True, nullable=True, description="The last updated at date when the supplement was last updated", alias="updated_at")
    description: Series[String] = pa.Field(coerce=True, nullable=True, description="The description of the supplement", alias="description")
    payroll_policy_period_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="The payroll policy period identifier associated with the supplement", alias="payroll_policy_period_id")
    employee_observations: Series[String] = pa.Field(coerce=True, nullable=True, description="Observations on the employee made by the admin or manager", alias="employee_observations")
    raw_minutes_in_cents: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="The raw value of minutes in cents associated with the supplement", alias="raw_minutes_in_cents")
    minutes_in_cents: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="The value of minutes in cents after adjustments", alias="minutes_in_cents")
    equivalent_minutes_in_cents: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="The equivalent value of minutes in cents for payroll processing", alias="equivalent_minutes_in_cents")
    currency: Series[String] = pa.Field(coerce=True, nullable=True, description="The currency used for the supplement, typically in ISO 4217 format", alias="currency")
    legal_entity_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="The legal entity identifier associated with the supplement", alias="legal_entity_id")

class Family_situationsCreate(BaseModel):
    employee_id: int = Field(..., description="Employee id.", alias="employee_id")
    civil_status: Optional[Annotated[str, StringConstraints(pattern=r'^single|cohabitating|divorced|married|civil_partnership|separated|widow|not_applicable|unknown$', strip_whitespace=True)]] = Field(None, description="Civil status of the employee.", alias="civil_status")
    number_of_dependants: Optional[int] = Field(None, description="Number of dependants of the employee.", alias="number_of_dependants")

class Family_situationsUpdate(BaseModel):
    id: int = Field(..., description="ID", alias="id")
    employee_id: int = Field(..., description="Employee id of the family situation.", alias="employee_id")
    civil_status: Optional[Annotated[str, StringConstraints(pattern=r'^single|cohabitating|divorced|married|unknown|civil_partnership|separated|widow|not_applicable$', strip_whitespace=True)]] = Field(None, description="Civil status of the employee.", alias="civil_status")
    number_of_dependants: Optional[int] = Field(None, description="Number of dependants of the employee.", alias="number_of_dependants")

class Family_situationsDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

class Policy_periodsCreate(BaseModel):
    id: int = Field(..., description="Policy period id", alias="id")
    name: Optional[str] = Field(None, description="Policy name with start and end date", alias="name")
    starts_on: str = Field(..., description="The start date of the policy period", alias="starts_on")
    policy_id: int = Field(..., description="The id of the policy associated with the policy period", alias="policy_id")
    company_id: int = Field(..., description="The id of the company", alias="company_id")
    ends_on: str = Field(..., description="The start date of the policy period", alias="ends_on")
    period: str = Field(..., description="Period for the policy", alias="period")
    status: Optional[str] = Field(None, description="Policy period status", alias="status")
    policy_name: Optional[str] = Field(None, description="Policy name", alias="policy_name")
    calculation_started_at: Optional[str] = Field(None, description="The date and time the calculation started", alias="calculation_started_at")

class Policy_periodsDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

class SupplementsCreate(BaseModel):
    amount_in_cents: int = Field(..., description="Supplement amount in cents", alias="amount_in_cents")
    employee_id: int = Field(..., description="The employee id of the suplement", alias="employee_id")
    effective_on: str = Field(..., description="Supplement effective on date following the format YYYY-MM-DD", alias="effective_on")
    contracts_compensation_id: Optional[int] = Field(None, description="The supplement contract compensation id", alias="contracts_compensation_id")
    contracts_taxonomy_id: int = Field(..., description="Supplement contract taxonomy id", alias="contracts_taxonomy_id")
    payroll_policy_period_id: int = Field(..., description="Supplement payroll policy period id", alias="payroll_policy_period_id")
    unit: Optional[str] = Field(None, description="Supplement unit", alias="unit")
    worked_days: Optional[int] = Field(None, description="Supplement worked days", alias="worked_days")

class SupplementsUpdate(BaseModel):
    id: int = Field(..., description="ID", alias="id")
    employee_id: int = Field(..., description="The identifier of the employee associated with the supplement", alias="employee_id")
    company_id: int = Field(..., description="The identifier of the company associated with the supplement", alias="company_id")
    contracts_compensation_id: Optional[int] = Field(None, description="The contract compensation identifier associated with the supplement", alias="contracts_compensation_id")
    contracts_taxonomy_id: Optional[int] = Field(None, description="The taxonomy identifier associated with the supplement", alias="contracts_taxonomy_id")
    amount_in_cents: Optional[int] = Field(None, description="The amount of the supplement in cents", alias="amount_in_cents")
    unit: Annotated[str, StringConstraints(pattern=r'^money|units|time$', strip_whitespace=True)] = Field(..., description="The unit of the supplement", alias="unit")
    effective_on: Optional[str] = Field(None, description="The date on which the supplement becomes effective", alias="effective_on")
    created_at: Optional[bool] = Field(None, description="The created at date when the supplement was created", alias="created_at")
    updated_at: Optional[bool] = Field(None, description="The last updated at date when the supplement was last updated", alias="updated_at")
    description: Optional[str] = Field(None, description="The description of the supplement", alias="description")
    payroll_policy_period_id: Optional[int] = Field(None, description="The payroll policy period identifier associated with the supplement", alias="payroll_policy_period_id")
    employee_observations: Optional[str] = Field(None, description="Observations on the employee made by the admin or manager", alias="employee_observations")
    raw_minutes_in_cents: Optional[int] = Field(None, description="The raw value of minutes in cents associated with the supplement", alias="raw_minutes_in_cents")
    minutes_in_cents: Optional[int] = Field(None, description="The value of minutes in cents after adjustments", alias="minutes_in_cents")
    equivalent_minutes_in_cents: Optional[int] = Field(None, description="The equivalent value of minutes in cents for payroll processing", alias="equivalent_minutes_in_cents")
    currency: Optional[str] = Field(None, description="The currency used for the supplement, typically in ISO 4217 format", alias="currency")
    legal_entity_id: Optional[int] = Field(None, description="The legal entity identifier associated with the supplement", alias="legal_entity_id")

class SupplementsDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

