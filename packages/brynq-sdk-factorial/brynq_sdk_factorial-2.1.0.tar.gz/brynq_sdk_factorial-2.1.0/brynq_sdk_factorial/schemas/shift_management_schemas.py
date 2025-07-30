# Auto-generated schemas for category: shift_management

import pandas as pd
import pandera as pa
from pandera.typing import Series, String, Int, Float, Bool, DateTime
import pandera.extensions as extensions
from brynq_sdk_functions import BrynQPanderaDataFrameModel
from typing import Optional, Annotated
from pydantic import BaseModel, Field, StringConstraints

class ShiftsGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Shift identifier", alias="id")
    company_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Company identifier", alias="company_id")
    name: Series[String] = pa.Field(coerce=True, nullable=True, description="Name of the shift", alias="name")
    state: Series[String] = pa.Field(coerce=True, nullable=False, description="The state of the shift.", alias="state")
    location_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="Shift location identifier", alias="location_id")
    locations_work_area_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="Shift work area identifier", alias="locations_work_area_id")
    employee_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Employee identifier", alias="employee_id")
    start_at: Series[String] = pa.Field(coerce=True, nullable=False, description="Start date of the shift", alias="start_at")
    end_at: Series[String] = pa.Field(coerce=True, nullable=False, description="End date of the shift", alias="end_at")
    notes: Series[String] = pa.Field(coerce=True, nullable=True, description="Shift notes", alias="notes")
    extra_hours: Series[Bool] = pa.Field(coerce=True, nullable=True, description="Flag to indicate if the shift has extra hours", alias="extra_hours")
    default_shift_title: Series[String] = pa.Field(coerce=True, nullable=True, description="Default shift title", alias="default_shift_title")
    timezone: Series[String] = pa.Field(coerce=True, nullable=False, description="Shift timezone", alias="timezone")
    local_start_at: Series[String] = pa.Field(coerce=True, nullable=False, description="Local start date of the shift", alias="local_start_at")
    local_end_at: Series[String] = pa.Field(coerce=True, nullable=False, description="Local end date of the shift", alias="local_end_at")

class ShiftsCreate(BaseModel):
    name: Optional[str] = Field(None, description="Name of the shift", alias="name")
    start_at: str = Field(..., description="Start date of the shift", alias="start_at")
    end_at: str = Field(..., description="End date of the shift", alias="end_at")
    notes: Optional[str] = Field(None, description="Shift notes", alias="notes")
    employee_id: int = Field(..., description="Employee identifier", alias="employee_id")
    location_id: Optional[int] = Field(None, description="Location identifier", alias="location_id")
    work_area_id: Optional[int] = Field(None, description="Location work area identifier", alias="work_area_id")
    company_id: int = Field(..., description="Company identifier", alias="company_id")

class ShiftsDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

