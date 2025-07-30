# Auto-generated schemas for category: employees

import pandas as pd
import pandera as pa
from pandera.typing import Series, String, Int, Float, Bool, DateTime
import pandera.extensions as extensions
from brynq_sdk_functions import BrynQPanderaDataFrameModel
from typing import Optional, Annotated
from pydantic import BaseModel, Field, StringConstraints

class EmployeesGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="id of the employee.", alias="id")
    access_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="access_id associated to the employee.", alias="access_id")
    first_name: Series[String] = pa.Field(coerce=True, nullable=False, description="name of the employee.", alias="first_name")
    last_name: Series[String] = pa.Field(coerce=True, nullable=False, description="last name of the employee.", alias="last_name")
    full_name: Series[String] = pa.Field(coerce=True, nullable=False, description="full name of the employee.", alias="full_name")
    preferred_name: Series[String] = pa.Field(coerce=True, nullable=True, description="nickname of the employee or a name that defines the employee better.", alias="preferred_name")
    birth_name: Series[String] = pa.Field(coerce=True, nullable=True, description="Birthname of the employee.", alias="birth_name")
    gender: Series[String] = pa.Field(coerce=True, nullable=True, description="gender of the employee (male | female).", alias="gender")
    identifier: Series[String] = pa.Field(coerce=True, nullable=True, description="national identifier number.", alias="identifier")
    identifier_type: Series[String] = pa.Field(coerce=True, nullable=True, description="type of identifier (ex passport).", alias="identifier_type")
    email: Series[String] = pa.Field(coerce=True, nullable=True, description="personal email of the employee.", alias="email")
    login_email: Series[String] = pa.Field(coerce=True, nullable=True, description="email associated to the session.", alias="login_email")
    birthday_on: Series[String] = pa.Field(coerce=True, nullable=True, description="birthday of the employee.", alias="birthday_on")
    nationality: Series[String] = pa.Field(coerce=True, nullable=True, description="nationality country code of the employee (Spain ES, United Kingdom GB).", alias="nationality")
    address_line_1: Series[String] = pa.Field(coerce=True, nullable=True, description="address of the employee.", alias="address_line_1")
    address_line_2: Series[String] = pa.Field(coerce=True, nullable=True, description="secondary address of the employee.", alias="address_line_2")
    postal_code: Series[String] = pa.Field(coerce=True, nullable=True, description="postal code of the employee.", alias="postal_code")
    city: Series[String] = pa.Field(coerce=True, nullable=True, description="city of the employee.", alias="city")
    state: Series[String] = pa.Field(coerce=True, nullable=True, description="state/province/region of the employee.", alias="state")
    country: Series[String] = pa.Field(coerce=True, nullable=True, description="country code of the employee (Spain ES, United Kingdom GB).", alias="country")
    bank_number: Series[String] = pa.Field(coerce=True, nullable=True, description="bank account number of the employee.", alias="bank_number")
    swift_bic: Series[String] = pa.Field(coerce=True, nullable=True, description="code to identify banks and financial institutions globally.", alias="swift_bic")
    bank_number_format: Series[String] = pa.Field(coerce=True, nullable=True, description="bank number format.", alias="bank_number_format")
    company_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="id of the company to which the employee belongs (not editable).", alias="company_id")
    legal_entity_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="legal entity of the employee, references to companies/legal_entities.", alias="legal_entity_id")
    location_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="location id of the employee, references to locations/locations.", alias="location_id")
    created_at: Series[String] = pa.Field(coerce=True, nullable=False, description="creation date of the employee.", alias="created_at")
    updated_at: Series[String] = pa.Field(coerce=True, nullable=False, description="date of last modification of the employee", alias="updated_at")
    social_security_number: Series[String] = pa.Field(coerce=True, nullable=True, description="social security number of the employee.", alias="social_security_number")
    is_terminating: Series[Bool] = pa.Field(coerce=True, nullable=False, description="is the employee being terminated?", alias="is_terminating")
    terminated_on: Series[String] = pa.Field(coerce=True, nullable=True, description="termination date of the employee.", alias="terminated_on")
    termination_reason_type: Series[String] = pa.Field(coerce=True, nullable=True, description="termination reason type of the employee", alias="termination_reason_type")
    termination_reason: Series[String] = pa.Field(coerce=True, nullable=True, description="A reason for the termination.", alias="termination_reason")
    termination_observations: Series[String] = pa.Field(coerce=True, nullable=True, description="observations about the termination.", alias="termination_observations")
    manager_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="manager id of the employee, you can get the manager id from employees endpoint.", alias="manager_id")
    timeoff_manager_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="Timeoff manager id of the employee.", alias="timeoff_manager_id")
    phone_number: Series[String] = pa.Field(coerce=True, nullable=True, description="phone number of the employee.", alias="phone_number")
    company_identifier: Series[String] = pa.Field(coerce=True, nullable=True, description="identity number or string used inside a company to internally identify the employee.", alias="company_identifier")
    age_number: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="age of the employee.", alias="age_number")
    termination_type_description: Series[String] = pa.Field(coerce=True, nullable=True, description="The description of the termination type.", alias="termination_type_description")
    contact_name: Series[String] = pa.Field(coerce=True, nullable=True, description="name of the employee contact.", alias="contact_name")
    contact_number: Series[String] = pa.Field(coerce=True, nullable=True, description="phone number of the employee contact .", alias="contact_number")
    personal_email: Series[String] = pa.Field(coerce=True, nullable=True, description="personal email of the employee.", alias="personal_email")
    seniority_calculation_date: Series[String] = pa.Field(coerce=True, nullable=True, description="date since when the employee is working in the company.", alias="seniority_calculation_date")
    pronouns: Series[String] = pa.Field(coerce=True, nullable=True, description="pronouns that an employee uses to define themselves.", alias="pronouns")
    active: Series[Bool] = pa.Field(coerce=True, nullable=True, description="status of the employee, true when active, false when terminated.", alias="active")
    disability_percentage_cents: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="officially certified level of disability granted by public administration for individuals with physical or mental impairments, expressed in cents", alias="disability_percentage_cents")
    identifier_expiration_date: Series[String] = pa.Field(coerce=True, nullable=True, description="identifier expiration date", alias="identifier_expiration_date")

    class _Annotation:
        primary_key = "id"
        foreign_keys = {
            "legal_entity_id": {
                "parent_schema": "Legal_entitiesGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "location_id": {
                "parent_schema": "LocationsGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "manager_id": {
                "parent_schema": "EmployeesGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "timeoff_manager_id": {
                "parent_schema": "EmployeesGet",
                "parent_column": "id",
                "cardinality": "N:1"
            }
        }

class EmployeesCreate(BaseModel):
    id: int = Field(..., description="id of the employee.", alias="id")
    access_id: int = Field(..., description="access_id associated to the employee.", alias="access_id")
    first_name: str = Field(..., description="name of the employee.", alias="first_name")
    last_name: str = Field(..., description="last name of the employee.", alias="last_name")
    full_name: str = Field(..., description="full name of the employee.", alias="full_name")
    preferred_name: Optional[str] = Field(None, description="nickname of the employee or a name that defines the employee better.", alias="preferred_name")
    birth_name: Optional[str] = Field(None, description="Birthname of the employee.", alias="birth_name")
    gender: Optional[str] = Field(None, description="gender of the employee (male | female).", alias="gender")
    identifier: Optional[str] = Field(None, description="national identifier number.", alias="identifier")
    identifier_type: Optional[str] = Field(None, description="type of identifier (ex passport).", alias="identifier_type")
    email: Optional[str] = Field(None, description="personal email of the employee.", alias="email")
    login_email: Optional[str] = Field(None, description="email associated to the session.", alias="login_email")
    birthday_on: Optional[str] = Field(None, description="birthday of the employee.", alias="birthday_on")
    nationality: Optional[str] = Field(None, description="nationality country code of the employee (Spain ES, United Kingdom GB).", alias="nationality")
    address_line_1: Optional[str] = Field(None, description="address of the employee.", alias="address_line_1")
    address_line_2: Optional[str] = Field(None, description="secondary address of the employee.", alias="address_line_2")
    postal_code: Optional[str] = Field(None, description="postal code of the employee.", alias="postal_code")
    city: Optional[str] = Field(None, description="city of the employee.", alias="city")
    state: Optional[str] = Field(None, description="state/province/region of the employee.", alias="state")
    country: Optional[str] = Field(None, description="country code of the employee (Spain ES, United Kingdom GB).", alias="country")
    bank_number: Optional[str] = Field(None, description="bank account number of the employee.", alias="bank_number")
    swift_bic: Optional[str] = Field(None, description="code to identify banks and financial institutions globally.", alias="swift_bic")
    bank_number_format: Optional[Annotated[str, StringConstraints(pattern=r'^iban|sort_code_and_account_number|routing_number_and_account_number|clabe|other|bank_name_and_account_number$', strip_whitespace=True)]] = Field(None, description="bank number format.", alias="bank_number_format")
    company_id: int = Field(..., description="id of the company to which the employee belongs (not editable).", alias="company_id")
    legal_entity_id: Optional[int] = Field(None, description="legal entity of the employee, references to companies/legal_entities.", alias="legal_entity_id")
    location_id: int = Field(..., description="location id of the employee, references to locations/locations.", alias="location_id")
    created_at: str = Field(..., description="creation date of the employee.", alias="created_at")
    updated_at: str = Field(..., description="date of last modification of the employee", alias="updated_at")
    social_security_number: Optional[str] = Field(None, description="social security number of the employee.", alias="social_security_number")
    is_terminating: bool = Field(..., description="is the employee being terminated?", alias="is_terminating")
    terminated_on: Optional[str] = Field(None, description="termination date of the employee.", alias="terminated_on")
    termination_reason_type: Optional[str] = Field(None, description="termination reason type of the employee", alias="termination_reason_type")
    termination_reason: Optional[str] = Field(None, description="A reason for the termination.", alias="termination_reason")
    termination_observations: Optional[str] = Field(None, description="observations about the termination.", alias="termination_observations")
    manager_id: Optional[int] = Field(None, description="manager id of the employee, you can get the manager id from employees endpoint.", alias="manager_id")
    timeoff_manager_id: Optional[int] = Field(None, description="Timeoff manager id of the employee.", alias="timeoff_manager_id")
    phone_number: Optional[str] = Field(None, description="phone number of the employee.", alias="phone_number")
    company_identifier: Optional[str] = Field(None, description="identity number or string used inside a company to internally identify the employee.", alias="company_identifier")
    age_number: Optional[int] = Field(None, description="age of the employee.", alias="age_number")
    termination_type_description: Optional[str] = Field(None, description="The description of the termination type.", alias="termination_type_description")
    contact_name: Optional[str] = Field(None, description="name of the employee contact.", alias="contact_name")
    contact_number: Optional[str] = Field(None, description="phone number of the employee contact .", alias="contact_number")
    personal_email: Optional[str] = Field(None, description="personal email of the employee.", alias="personal_email")
    seniority_calculation_date: Optional[str] = Field(None, description="date since when the employee is working in the company.", alias="seniority_calculation_date")
    pronouns: Optional[str] = Field(None, description="pronouns that an employee uses to define themselves.", alias="pronouns")
    active: Optional[bool] = Field(None, description="status of the employee, true when active, false when terminated.", alias="active")
    disability_percentage_cents: Optional[int] = Field(None, description="officially certified level of disability granted by public administration for individuals with physical or mental impairments, expressed in cents", alias="disability_percentage_cents")
    identifier_expiration_date: Optional[str] = Field(None, description="identifier expiration date", alias="identifier_expiration_date")

class EmployeesUpdate(BaseModel):
    id: int = Field(..., description="ID", alias="id")
    access_id: int = Field(..., description="access_id associated to the employee.", alias="access_id")
    first_name: str = Field(..., description="name of the employee.", alias="first_name")
    last_name: str = Field(..., description="last name of the employee.", alias="last_name")
    full_name: str = Field(..., description="full name of the employee.", alias="full_name")
    preferred_name: Optional[str] = Field(None, description="nickname of the employee or a name that defines the employee better.", alias="preferred_name")
    birth_name: Optional[str] = Field(None, description="Birthname of the employee.", alias="birth_name")
    gender: Optional[str] = Field(None, description="gender of the employee (male | female).", alias="gender")
    identifier: Optional[str] = Field(None, description="national identifier number.", alias="identifier")
    identifier_type: Optional[str] = Field(None, description="type of identifier (ex passport).", alias="identifier_type")
    email: Optional[str] = Field(None, description="personal email of the employee.", alias="email")
    login_email: Optional[str] = Field(None, description="email associated to the session.", alias="login_email")
    birthday_on: Optional[str] = Field(None, description="birthday of the employee.", alias="birthday_on")
    nationality: Optional[str] = Field(None, description="nationality country code of the employee (Spain ES, United Kingdom GB).", alias="nationality")
    address_line_1: Optional[str] = Field(None, description="address of the employee.", alias="address_line_1")
    address_line_2: Optional[str] = Field(None, description="secondary address of the employee.", alias="address_line_2")
    postal_code: Optional[str] = Field(None, description="postal code of the employee.", alias="postal_code")
    city: Optional[str] = Field(None, description="city of the employee.", alias="city")
    state: Optional[str] = Field(None, description="state/province/region of the employee.", alias="state")
    country: Optional[str] = Field(None, description="country code of the employee (Spain ES, United Kingdom GB).", alias="country")
    bank_number: Optional[str] = Field(None, description="bank account number of the employee.", alias="bank_number")
    swift_bic: Optional[str] = Field(None, description="code to identify banks and financial institutions globally.", alias="swift_bic")
    bank_number_format: Optional[Annotated[str, StringConstraints(pattern=r'^iban|sort_code_and_account_number|routing_number_and_account_number|clabe|other|bank_name_and_account_number$', strip_whitespace=True)]] = Field(None, description="bank number format.", alias="bank_number_format")
    company_id: int = Field(..., description="id of the company to which the employee belongs (not editable).", alias="company_id")
    legal_entity_id: Optional[int] = Field(None, description="legal entity of the employee, references to companies/legal_entities.", alias="legal_entity_id")
    location_id: int = Field(..., description="location id of the employee, references to locations/locations.", alias="location_id")
    created_at: str = Field(..., description="creation date of the employee.", alias="created_at")
    updated_at: str = Field(..., description="date of last modification of the employee", alias="updated_at")
    social_security_number: Optional[str] = Field(None, description="social security number of the employee.", alias="social_security_number")
    is_terminating: bool = Field(..., description="is the employee being terminated?", alias="is_terminating")
    terminated_on: Optional[str] = Field(None, description="termination date of the employee.", alias="terminated_on")
    termination_reason_type: Optional[str] = Field(None, description="termination reason type of the employee", alias="termination_reason_type")
    termination_reason: Optional[str] = Field(None, description="A reason for the termination.", alias="termination_reason")
    termination_observations: Optional[str] = Field(None, description="observations about the termination.", alias="termination_observations")
    manager_id: Optional[int] = Field(None, description="manager id of the employee, you can get the manager id from employees endpoint.", alias="manager_id")
    timeoff_manager_id: Optional[int] = Field(None, description="Timeoff manager id of the employee.", alias="timeoff_manager_id")
    phone_number: Optional[str] = Field(None, description="phone number of the employee.", alias="phone_number")
    company_identifier: Optional[str] = Field(None, description="identity number or string used inside a company to internally identify the employee.", alias="company_identifier")
    age_number: Optional[int] = Field(None, description="age of the employee.", alias="age_number")
    termination_type_description: Optional[str] = Field(None, description="The description of the termination type.", alias="termination_type_description")
    contact_name: Optional[str] = Field(None, description="name of the employee contact.", alias="contact_name")
    contact_number: Optional[str] = Field(None, description="phone number of the employee contact .", alias="contact_number")
    personal_email: Optional[str] = Field(None, description="personal email of the employee.", alias="personal_email")
    seniority_calculation_date: Optional[str] = Field(None, description="date since when the employee is working in the company.", alias="seniority_calculation_date")
    pronouns: Optional[str] = Field(None, description="pronouns that an employee uses to define themselves.", alias="pronouns")
    active: Optional[bool] = Field(None, description="status of the employee, true when active, false when terminated.", alias="active")
    disability_percentage_cents: Optional[int] = Field(None, description="officially certified level of disability granted by public administration for individuals with physical or mental impairments, expressed in cents", alias="disability_percentage_cents")
    identifier_expiration_date: Optional[str] = Field(None, description="identifier expiration date", alias="identifier_expiration_date")

class EmployeesDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")
