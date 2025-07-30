# Auto-generated schemas for category: time_settings

import pandas as pd
import pandera as pa
from pandera.typing import Series, String, Int, Float, Bool, DateTime
import pandera.extensions as extensions
from brynq_sdk_functions import BrynQPanderaDataFrameModel
from typing import Optional, Annotated
from pydantic import BaseModel, Field, StringConstraints

class Break_configurationsGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="", alias="id")
    name: Series[String] = pa.Field(coerce=True, nullable=False, description="", alias="name")
    paid: Series[Bool] = pa.Field(coerce=True, nullable=False, description="", alias="paid")
    archived: Series[Bool] = pa.Field(coerce=True, nullable=False, description="", alias="archived")

class Break_configurationsCreate(BaseModel):
    name: str = Field(..., description="", alias="name")
    paid: bool = Field(..., description="", alias="paid")

class Break_configurationsUpdate(BaseModel):
    id: int = Field(..., description="ID", alias="id")
    name: str = Field(..., description="", alias="name")
    paid: bool = Field(..., description="", alias="paid")
    archived: bool = Field(..., description="", alias="archived")

class Break_configurationsDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

