# Auto-generated schemas for category: locations

import pandas as pd
import pandera as pa
from pandera.typing import Series, String, Int, Float, Bool, DateTime
import pandera.extensions as extensions
from brynq_sdk_functions import BrynQPanderaDataFrameModel
from typing import Optional, Annotated
from pydantic import BaseModel, Field, StringConstraints

class LocationsGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="identifier of the location", alias="id")
    company_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="company identifier", alias="company_id")
    name: Series[String] = pa.Field(coerce=True, nullable=False, description="name of the location", alias="name")
    timezone: Series[String] = pa.Field(coerce=True, nullable=True, description="timezone of the location", alias="timezone")
    country: Series[String] = pa.Field(coerce=True, nullable=True, description="country code of the location", alias="country")
    state: Series[String] = pa.Field(coerce=True, nullable=True, description="State of the location", alias="state")
    city: Series[String] = pa.Field(coerce=True, nullable=True, description="City of the location", alias="city")
    address_line_1: Series[String] = pa.Field(coerce=True, nullable=True, description="Address line 1 of the location", alias="address_line_1")
    address_line_2: Series[String] = pa.Field(coerce=True, nullable=True, description="Address line 2 of the location", alias="address_line_2")
    postal_code: Series[String] = pa.Field(coerce=True, nullable=True, description="Postal code of the location", alias="postal_code")
    phone_number: Series[String] = pa.Field(coerce=True, nullable=True, description="phone number of the location", alias="phone_number")
    main: Series[Bool] = pa.Field(coerce=True, nullable=False, description="whether the location is the main one", alias="main")
    latitude: Series[Float] = pa.Field(coerce=True, nullable=True, description="latitude of the location", alias="latitude")
    longitude: Series[Float] = pa.Field(coerce=True, nullable=True, description="longitude of the location", alias="longitude")
    radius: Series[Float] = pa.Field(coerce=True, nullable=True, description="radius of the location", alias="radius")
    siret: Series[String] = pa.Field(coerce=True, nullable=True, description="siret of the location (only for France)", alias="siret")

class Work_areasGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="", alias="id")
    location_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="", alias="location_id")
    name: Series[String] = pa.Field(coerce=True, nullable=False, description="", alias="name")
    archived_at: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="archived_at")

class LocationsCreate(BaseModel):
    name: str = Field(..., description="name of the location", alias="name")
    country: str = Field(..., description="country code of the location", alias="country")
    main: Optional[bool] = Field(None, description="whether the location is the main one", alias="main")
    city: Optional[str] = Field(None, description="City of the location", alias="city")
    state: Optional[str] = Field(None, description="State of the location", alias="state")
    phone_number: Optional[str] = Field(None, description="phone number of the location", alias="phone_number")
    postal_code: Optional[str] = Field(None, description="Postal code of the location", alias="postal_code")
    address_line_one: Optional[str] = Field(None, description="Address line 1 of the location", alias="address_line_one")
    address_line_two: Optional[str] = Field(None, description="Address line 2 of the location", alias="address_line_two")
    latitude: Optional[float] = Field(None, description="latitude of the location", alias="latitude")
    longitude: Optional[float] = Field(None, description="longitude of the location", alias="longitude")
    timezone: str = Field(..., description="timezone of the location", alias="timezone")
    radius: Optional[float] = Field(None, description="radius of the location", alias="radius")
    company_id: int = Field(..., description="company identifier", alias="company_id")
    siret: Optional[str] = Field(None, description="siret of the location (only for France)", alias="siret")

class LocationsUpdate(BaseModel):
    id: int = Field(..., description="ID", alias="id")
    company_id: int = Field(..., description="company identifier", alias="company_id")
    name: str = Field(..., description="name of the location", alias="name")
    timezone: Optional[str] = Field(None, description="timezone of the location", alias="timezone")
    country: Optional[str] = Field(None, description="country code of the location", alias="country")
    state: Optional[str] = Field(None, description="State of the location", alias="state")
    city: Optional[str] = Field(None, description="City of the location", alias="city")
    address_line_1: Optional[str] = Field(None, description="Address line 1 of the location", alias="address_line_1")
    address_line_2: Optional[str] = Field(None, description="Address line 2 of the location", alias="address_line_2")
    postal_code: Optional[str] = Field(None, description="Postal code of the location", alias="postal_code")
    phone_number: Optional[str] = Field(None, description="phone number of the location", alias="phone_number")
    main: bool = Field(..., description="whether the location is the main one", alias="main")
    latitude: Optional[float] = Field(None, description="latitude of the location", alias="latitude")
    longitude: Optional[float] = Field(None, description="longitude of the location", alias="longitude")
    radius: Optional[float] = Field(None, description="radius of the location", alias="radius")
    siret: Optional[str] = Field(None, description="siret of the location (only for France)", alias="siret")

class LocationsDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

class Work_areasCreate(BaseModel):
    name: str = Field(..., description="", alias="name")
    location_id: int = Field(..., description="", alias="location_id")

class Work_areasUpdate(BaseModel):
    id: int = Field(..., description="ID", alias="id")
    location_id: int = Field(..., description="", alias="location_id")
    name: str = Field(..., description="", alias="name")
    archived_at: Optional[str] = Field(None, description="", alias="archived_at")

class Work_areasDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

