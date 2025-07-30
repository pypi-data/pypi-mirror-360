# Auto-generated schemas for category: job_catalog

import pandas as pd
import pandera as pa
from pandera.typing import Series, String, Int, Float, Bool, DateTime
import pandera.extensions as extensions
from brynq_sdk_functions import BrynQPanderaDataFrameModel
from typing import Optional, Annotated
from pydantic import BaseModel, Field, StringConstraints

class LevelsGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="identifier for the job catalog level.", alias="id")
    role_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="identifier for the job catalog role.", alias="role_id")
    name: Series[String] = pa.Field(coerce=True, nullable=False, description="Level name.", alias="name")
    role_name: Series[String] = pa.Field(coerce=True, nullable=False, description="Role name.", alias="role_name")
    order: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Order of the level.", alias="order")
    archived: Series[Bool] = pa.Field(coerce=True, nullable=False, description="Shows if the role is archived.", alias="archived")
    is_default: Series[Bool] = pa.Field(coerce=True, nullable=False, description="Shows if the level is the default one.", alias="is_default")

class RolesGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="identifier for the job catalog role.", alias="id")
    company_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Identifier for the company.", alias="company_id")
    name: Series[String] = pa.Field(coerce=True, nullable=False, description="Role name.", alias="name")
    description: Series[String] = pa.Field(coerce=True, nullable=True, description="Role description.", alias="description")
    legal_entities_ids: Series[String] = pa.Field(coerce=True, nullable=False, description="List of legal entities.", alias="legal_entities_ids")
    supervisors_ids: Series[String] = pa.Field(coerce=True, nullable=True, description="List of supervisors.", alias="supervisors_ids")
    competencies_ids: Series[String] = pa.Field(coerce=True, nullable=True, description="List of competencies.", alias="competencies_ids")
    archived: Series[Bool] = pa.Field(coerce=True, nullable=False, description="Shows if the role is archived.", alias="archived")

class LevelsDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

class RolesDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

