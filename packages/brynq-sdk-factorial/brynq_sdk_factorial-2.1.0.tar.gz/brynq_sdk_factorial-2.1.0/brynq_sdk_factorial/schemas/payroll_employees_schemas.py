# Auto-generated schemas for category: payroll_employees

import pandas as pd
import pandera as pa
from pandera.typing import Series, String, Int, Float, Bool, DateTime
import pandera.extensions as extensions
from brynq_sdk_functions import BrynQPanderaDataFrameModel
from typing import Optional, Annotated
from pydantic import BaseModel, Field, StringConstraints

class IdentifiersGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="payroll employee identifier", alias="id")
    employee_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="identifier of the employee", alias="employee_id")
    social_security_number: Series[String] = pa.Field(coerce=True, nullable=True, description="social security number of the employee", alias="social_security_number")
    tax_id: Series[String] = pa.Field(coerce=True, nullable=True, description="tax id of the employee", alias="tax_id")
    country: Series[String] = pa.Field(coerce=True, nullable=False, description="country code of the employee pt | it | de", alias="country")

class IdentifiersCreate(BaseModel):
    employee_id: int = Field(..., description="identifier of the employee", alias="employee_id")
    social_security_number: Optional[str] = Field(None, description="social security number of the employee", alias="social_security_number")
    tax_id: Optional[str] = Field(None, description="tax id of the employee", alias="tax_id")
    country: Annotated[str, StringConstraints(pattern=r'^pt|de|it$', strip_whitespace=True)] = Field(..., description="country code of the employee pt | it | de", alias="country")

class IdentifiersUpdate(BaseModel):
    id: int = Field(..., description="ID", alias="id")
    employee_id: int = Field(..., description="identifier of the employee", alias="employee_id")
    social_security_number: Optional[str] = Field(None, description="social security number of the employee", alias="social_security_number")
    tax_id: Optional[str] = Field(None, description="tax id of the employee", alias="tax_id")
    country: Annotated[str, StringConstraints(pattern=r'^pt|de|it$', strip_whitespace=True)] = Field(..., description="country code of the employee pt | it | de", alias="country")

class IdentifiersDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

