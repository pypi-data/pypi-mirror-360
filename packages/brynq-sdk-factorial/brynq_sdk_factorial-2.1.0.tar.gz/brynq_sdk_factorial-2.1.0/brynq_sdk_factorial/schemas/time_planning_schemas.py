# Auto-generated schemas for category: time_planning

import pandas as pd
import pandera as pa
from pandera.typing import Series, String, Int, Float, Bool, DateTime
import pandera.extensions as extensions
from brynq_sdk_functions import BrynQPanderaDataFrameModel
from typing import Optional, Annotated
from pydantic import BaseModel, Field, StringConstraints

class Planning_versionsCreate(BaseModel):
    effective_at: str = Field(..., description="Start date of the planning version", alias="effective_at")
    planning_tool: str = Field(..., description="Type of planning tool (shift_management, work_schedules, contract_hours)", alias="planning_tool")
    number_of_rest_days_in_cents: Optional[int] = Field(None, description="Amount of rest days per week if applicable (in cents)", alias="number_of_rest_days_in_cents")
    employee_id: int = Field(..., description="Employee identifier", alias="employee_id")
    schedule_id: Optional[int] = Field(None, description="Work schedule identifier to include if applicable", alias="schedule_id")

class Planning_versionsUpdate(BaseModel):
    id: int = Field(..., description="ID", alias="id")
    effective_at: str = Field(..., description="Start date of the planning version", alias="effective_at")
    planning_tool: str = Field(..., description="Type of planning tool (shift_management, work_schedules, contract_hours)", alias="planning_tool")
    number_of_rest_days_in_cents: Optional[int] = Field(None, description="Amount of rest days per week if applicable (in cents)", alias="number_of_rest_days_in_cents")
    employee_id: int = Field(..., description="Employee identifier", alias="employee_id")
    work_schedule_schedule_id: Optional[int] = Field(None, description="Work schedule identifier to include if applicable", alias="work_schedule_schedule_id")

class Planning_versionsDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

