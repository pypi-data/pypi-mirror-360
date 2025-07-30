# Auto-generated schemas for category: companies

import pandas as pd
import pandera as pa
from pandera.typing import Series, String, Int, Float, Bool, DateTime
import pandera.extensions as extensions
from brynq_sdk_functions import BrynQPanderaDataFrameModel
from typing import Optional, Annotated
from pydantic import BaseModel, Field, StringConstraints

class Legal_entitiesGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="identifier of the legal entity", alias="id")
    company_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="company identifier", alias="company_id")
    country: Series[String] = pa.Field(coerce=True, nullable=False, description="country code of the legal entity", alias="country")
    legal_name: Series[String] = pa.Field(coerce=True, nullable=False, description="Legal name of the legal entity", alias="legal_name")
    currency: Series[String] = pa.Field(coerce=True, nullable=False, description="The currency code in ISO 4217 format", alias="currency")
    tin: Series[String] = pa.Field(coerce=True, nullable=True, description="Tax identification number", alias="tin")
    city: Series[String] = pa.Field(coerce=True, nullable=True, description="City of the legal entity", alias="city")
    state: Series[String] = pa.Field(coerce=True, nullable=True, description="State of the legal entity", alias="state")
    postal_code: Series[String] = pa.Field(coerce=True, nullable=True, description="Postal code of the legal entity", alias="postal_code")
    address_line_1: Series[String] = pa.Field(coerce=True, nullable=True, description="Address line 1 of the legal entity", alias="address_line_1")
    address_line_2: Series[String] = pa.Field(coerce=True, nullable=True, description="Address line 2 of the legal entity", alias="address_line_2")

    class _Annotation:
        primary_key = "id"
        foreign_keys = {}

class Legal_entitiesDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")
