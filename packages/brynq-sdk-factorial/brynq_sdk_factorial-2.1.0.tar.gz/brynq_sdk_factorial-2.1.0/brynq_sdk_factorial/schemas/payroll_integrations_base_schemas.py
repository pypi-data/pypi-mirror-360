# Auto-generated schemas for category: payroll_integrations_base

import pandas as pd
import pandera as pa
from pandera.typing import Series, String, Int, Float, Bool, DateTime
import pandera.extensions as extensions
from brynq_sdk_functions import BrynQPanderaDataFrameModel
from typing import Optional, Annotated
from pydantic import BaseModel, Field, StringConstraints

class CodesCreate(BaseModel):
    code: str = Field(..., description="Code Value", alias="code")
    codeable_id: int = Field(..., description="Related object ID. Used together with codeable_type", alias="codeable_id")
    codeable_type: str = Field(..., description="Related object type. Used together with codeable_id", alias="codeable_type")
    integration: Annotated[str, StringConstraints(pattern=r'^a3innuva|a3nom|paierh|yeap_paierh|silae|silae_api|datev|datev_api|datev_lug_api|datev_lauds|zucchetti$', strip_whitespace=True)] = Field(..., description="Integration name", alias="integration")

class CodesUpdate(BaseModel):
    id: int = Field(..., description="ID", alias="id")
    company_id: int = Field(..., description="Company ID where the code belongs to", alias="company_id")
    code: str = Field(..., description="Code value", alias="code")
    codeable_id: int = Field(..., description="Related object ID. Used together with codeable_type", alias="codeable_id")
    codeable_type: str = Field(..., description="Related object type. Used together with codeable_id", alias="codeable_type")
    integration: Annotated[str, StringConstraints(pattern=r'^a3innuva|a3nom|paierh|yeap_paierh|silae|silae_api|datev|datev_api|datev_lug_api|datev_lauds|zucchetti$', strip_whitespace=True)] = Field(..., description="Integration name", alias="integration")

class CodesDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

