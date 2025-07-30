# Auto-generated schemas for category: teams

import pandas as pd
import pandera as pa
from pandera.typing import Series, String, Int, Float, Bool, DateTime
import pandera.extensions as extensions
from brynq_sdk_functions import BrynQPanderaDataFrameModel
from typing import Optional, Annotated
from pydantic import BaseModel, Field, StringConstraints

class MembershipsGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Membership ID", alias="id")
    company_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="Company ID of the membership", alias="company_id")
    employee_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Employee ID of the membership", alias="employee_id")
    team_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Team ID of the membership", alias="team_id")
    lead: Series[Bool] = pa.Field(coerce=True, nullable=False, description="Whether the employee is a lead of the team or not", alias="lead")

class TeamsGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="", alias="id")
    name: Series[String] = pa.Field(coerce=True, nullable=False, description="", alias="name")
    description: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="description")
    avatar: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="avatar")
    employee_ids: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="employee_ids")
    lead_ids: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="lead_ids")
    company_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="", alias="company_id")

class MembershipsCreate(BaseModel):
    team_id: int = Field(..., description="Team id.", alias="team_id")
    employee_id: int = Field(..., description="Employee id.", alias="employee_id")
    lead: Optional[bool] = Field(None, description="Makes the employee a lead of the team.", alias="lead")

class MembershipsUpdate(BaseModel):
    id: int = Field(..., description="ID", alias="id")
    company_id: Optional[int] = Field(None, description="Company ID of the membership", alias="company_id")
    employee_id: int = Field(..., description="Employee ID of the membership", alias="employee_id")
    team_id: int = Field(..., description="Team ID of the membership", alias="team_id")
    lead: bool = Field(..., description="Whether the employee is a lead of the team or not", alias="lead")

class MembershipsDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

class TeamsCreate(BaseModel):
    name: str = Field(..., description="Name of the team.", alias="name")
    description: Optional[str] = Field(None, description="Description of the team", alias="description")

class TeamsUpdate(BaseModel):
    id: int = Field(..., description="ID", alias="id")
    name: str = Field(..., description="", alias="name")
    description: Optional[str] = Field(None, description="", alias="description")
    avatar: Optional[str] = Field(None, description="", alias="avatar")
    employee_ids: Optional[str] = Field(None, description="", alias="employee_ids")
    lead_ids: Optional[str] = Field(None, description="", alias="lead_ids")
    company_id: int = Field(..., description="", alias="company_id")

class TeamsDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

