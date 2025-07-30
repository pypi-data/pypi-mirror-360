# Auto-generated schemas for category: work_schedule

import pandas as pd
import pandera as pa
from pandera.typing import Series, String, Int, Float, Bool, DateTime
import pandera.extensions as extensions
from brynq_sdk_functions import BrynQPanderaDataFrameModel
from typing import Optional, Annotated
from pydantic import BaseModel, Field, StringConstraints

class Day_configurationsGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="", alias="id")
    overlap_period_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="", alias="overlap_period_id")
    weekday: Series[String] = pa.Field(coerce=True, nullable=False, description="", alias="weekday")
    start_at: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="start_at")
    duration_in_seconds: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="", alias="duration_in_seconds")

class Overlap_periodsGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="", alias="id")
    default: Series[Bool] = pa.Field(coerce=True, nullable=False, description="", alias="default")
    schedule_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="", alias="schedule_id")
    start_month: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="", alias="start_month")
    start_day: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="", alias="start_day")
    end_month: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="", alias="end_month")
    end_day: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="", alias="end_day")
    schedule_type: Series[String] = pa.Field(coerce=True, nullable=False, description="", alias="schedule_type")

class SchedulesGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="", alias="id")
    name: Series[String] = pa.Field(coerce=True, nullable=False, description="", alias="name")
    archived_at: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="archived_at")
    company_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="", alias="company_id")
    created_at: Series[String] = pa.Field(coerce=True, nullable=False, description="", alias="created_at")
    updated_at: Series[String] = pa.Field(coerce=True, nullable=False, description="", alias="updated_at")
    employee_ids: Series[String] = pa.Field(coerce=True, nullable=False, description="", alias="employee_ids")
    periods: Series[String] = pa.Field(coerce=True, nullable=False, description="", alias="periods")

class Day_configurationsCreate(BaseModel):
    id: int = Field(..., description="", alias="id")
    overlap_period_id: int = Field(..., description="", alias="overlap_period_id")
    weekday: str = Field(..., description="", alias="weekday")
    start_at: Optional[str] = Field(None, description="", alias="start_at")
    duration_in_seconds: int = Field(..., description="", alias="duration_in_seconds")

class Day_configurationsDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

class Overlap_periodsCreate(BaseModel):
    author: str = Field(..., description="", alias="author")
    schedule_id: int = Field(..., description="", alias="schedule_id")
    create_params: str = Field(..., description="", alias="create_params")

class Overlap_periodsUpdate(BaseModel):
    id: int = Field(..., description="ID", alias="id")
    default: bool = Field(..., description="", alias="default")
    schedule_id: int = Field(..., description="", alias="schedule_id")
    start_month: int = Field(..., description="", alias="start_month")
    start_day: int = Field(..., description="", alias="start_day")
    end_month: int = Field(..., description="", alias="end_month")
    end_day: int = Field(..., description="", alias="end_day")
    schedule_type: str = Field(..., description="", alias="schedule_type")

class Overlap_periodsDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

class SchedulesCreate(BaseModel):
    name: str = Field(..., description="", alias="name")
    schedule_type: str = Field(..., description="", alias="schedule_type")

class SchedulesUpdate(BaseModel):
    id: int = Field(..., description="ID", alias="id")
    name: str = Field(..., description="", alias="name")
    archived_at: Optional[str] = Field(None, description="", alias="archived_at")
    company_id: int = Field(..., description="", alias="company_id")
    created_at: str = Field(..., description="", alias="created_at")
    updated_at: str = Field(..., description="", alias="updated_at")
    employee_ids: str = Field(..., description="", alias="employee_ids")
    periods: str = Field(..., description="", alias="periods")

class SchedulesDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

