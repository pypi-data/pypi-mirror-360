# Auto-generated schemas for category: holidays

import pandas as pd
import pandera as pa
from pandera.typing import Series, String, Int, Float, Bool, DateTime
import pandera.extensions as extensions
from brynq_sdk_functions import BrynQPanderaDataFrameModel
from typing import Optional, Annotated
from pydantic import BaseModel, Field, StringConstraints

class Company_holidaysGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Company holiday id", alias="id")
    location_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Related location id", alias="location_id")
    summary: Series[String] = pa.Field(coerce=True, nullable=True, description="Company holiday summary", alias="summary")
    description: Series[String] = pa.Field(coerce=True, nullable=True, description="Company holiday description", alias="description")
    date: Series[String] = pa.Field(coerce=True, nullable=False, description="Company holiday date", alias="date")
    half_day: Series[String] = pa.Field(coerce=True, nullable=True, description="If the company holiday is half-day and which part of the day", alias="half_day")

class Company_holidaysDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

