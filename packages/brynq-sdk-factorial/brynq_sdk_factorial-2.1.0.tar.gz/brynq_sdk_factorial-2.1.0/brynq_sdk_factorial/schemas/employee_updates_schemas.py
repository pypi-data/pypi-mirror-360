# Auto-generated schemas for category: employee_updates

import pandas as pd
import pandera as pa
from pandera.typing import Series, String, Int, Float, Bool, DateTime
import pandera.extensions as extensions
from brynq_sdk_functions import BrynQPanderaDataFrameModel
from typing import Optional, Annotated
from pydantic import BaseModel, Field, StringConstraints

class AbsencesGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="", alias="id")
    status: Series[String] = pa.Field(coerce=True, nullable=False, description="", alias="status")
    employee_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="", alias="employee_id")
    employee_full_name: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="employee_full_name")
    approved: Series[Bool] = pa.Field(coerce=True, nullable=True, description="", alias="approved")
    description: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="description")
    start_on: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="start_on")
    prev_start_on: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="prev_start_on")
    finish_on: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="finish_on")
    prev_finish_on: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="prev_finish_on")
    half_day: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="half_day")
    leave_type_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="", alias="leave_type_id")
    leave_type_name: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="leave_type_name")

    class _Annotation:
        primary_key = "id"
        foreign_keys = {
            "employee_id": {
                "parent_schema": "EmployeesGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "leave_type_id": {
                "parent_schema": "Leave_typesGet",
                "parent_column": "id",
                "cardinality": "N:1"
            }
        }

class Contract_changesGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="The id of the contract change incidence", alias="id")
    status: Series[String] = pa.Field(coerce=True, nullable=False, description="The status of the contract change incidence", alias="status")
    effective_on: Series[String] = pa.Field(coerce=True, nullable=False, description="The effective date of the contract", alias="effective_on")
    starts_on: Series[String] = pa.Field(coerce=True, nullable=True, description="The start date of the contract", alias="starts_on")
    ends_on: Series[String] = pa.Field(coerce=True, nullable=True, description="The end date of the contract", alias="ends_on")
    employee_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="The employee id", alias="employee_id")
    job_title: Series[String] = pa.Field(coerce=True, nullable=True, description="The job title on the contract change", alias="job_title")
    job_role: Series[String] = pa.Field(coerce=True, nullable=True, description="The job role on the contract change", alias="job_role")
    job_level: Series[String] = pa.Field(coerce=True, nullable=True, description="The job level on the contract change", alias="job_level")
    has_payroll: Series[Bool] = pa.Field(coerce=True, nullable=False, description="The payrollable status of the employee on the contract change", alias="has_payroll")
    salary_amount: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="The salary amount on the contract change", alias="salary_amount")
    salary_frequency: Series[String] = pa.Field(coerce=True, nullable=True, description="The salary payment frequency on the contract change", alias="salary_frequency")
    working_week_days: Series[String] = pa.Field(coerce=True, nullable=True, description="The working week days on the contract change", alias="working_week_days")
    working_hours: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="The working hours on the contract change", alias="working_hours")
    working_hours_frequency: Series[String] = pa.Field(coerce=True, nullable=True, description="The working hours frequency on the contract change", alias="working_hours_frequency")
    country: Series[String] = pa.Field(coerce=True, nullable=True, description="The country on the contract change", alias="country")
    es_has_teleworking_contract: Series[Bool] = pa.Field(coerce=True, nullable=True, description="The teleworking status on the contract change", alias="es_has_teleworking_contract")
    es_cotization_group: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="The cotization group on the contract change", alias="es_cotization_group")
    es_contract_observations: Series[String] = pa.Field(coerce=True, nullable=True, description="The contract observations on the contract change", alias="es_contract_observations")
    es_job_description: Series[String] = pa.Field(coerce=True, nullable=True, description="The job description on the contract change", alias="es_job_description")
    es_contract_type_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="The contract type id on the contract change", alias="es_contract_type_id")
    es_contract_type_name: Series[String] = pa.Field(coerce=True, nullable=True, description="The contract type name on the contract change", alias="es_contract_type_name")
    es_trial_period_ends_on: Series[String] = pa.Field(coerce=True, nullable=True, description="The trial period end date on the contract change", alias="es_trial_period_ends_on")
    es_working_day_type_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="The working day type id on the contract change", alias="es_working_day_type_id")
    es_education_level_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="The education level id on the contract change", alias="es_education_level_id")
    es_professional_category_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="The professional category id on the contract change", alias="es_professional_category_id")
    fr_employee_type: Series[String] = pa.Field(coerce=True, nullable=True, description="The employee type on the contract change", alias="fr_employee_type")
    fr_forfait_jours: Series[Bool] = pa.Field(coerce=True, nullable=False, description="The forfait jours status on the contract change", alias="fr_forfait_jours")
    fr_jours_par_an: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="The jours par an on the contract change", alias="fr_jours_par_an")
    fr_coefficient: Series[String] = pa.Field(coerce=True, nullable=True, description="The coefficient on the contract change", alias="fr_coefficient")
    fr_level_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="The level id on the contract change", alias="fr_level_id")
    fr_level_name: Series[String] = pa.Field(coerce=True, nullable=True, description="The level name on the contract change", alias="fr_level_name")
    fr_step_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="The step id on the contract change", alias="fr_step_id")
    fr_step_name: Series[String] = pa.Field(coerce=True, nullable=True, description="The step name on the contract change", alias="fr_step_name")
    fr_mutual_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="The mutual id on the contract change", alias="fr_mutual_id")
    fr_mutual_name: Series[String] = pa.Field(coerce=True, nullable=True, description="The mutual name on the contract change", alias="fr_mutual_name")
    fr_professional_category_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="The professional category id on the contract change", alias="fr_professional_category_id")
    fr_professional_category_name: Series[String] = pa.Field(coerce=True, nullable=True, description="The professional category name on the contract change", alias="fr_professional_category_name")
    fr_work_type_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="The work type id on the contract change", alias="fr_work_type_id")
    fr_work_type_name: Series[String] = pa.Field(coerce=True, nullable=True, description="The work type name on the contract change", alias="fr_work_type_name")
    compensation_ids: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="compensation_ids")
    fr_contract_type_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="The contract type id on the contract change", alias="fr_contract_type_id")
    fr_contract_type_name: Series[String] = pa.Field(coerce=True, nullable=True, description="The contract type name on the contract change", alias="fr_contract_type_name")
    de_contract_type_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="The contract type id on the contract change", alias="de_contract_type_id")
    de_contract_type_name: Series[String] = pa.Field(coerce=True, nullable=True, description="The contract type name on the contract change", alias="de_contract_type_name")
    pt_contract_type_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="The contract type id on the contract change", alias="pt_contract_type_id")
    pt_contract_type_name: Series[String] = pa.Field(coerce=True, nullable=True, description="The contract type name on the contract change", alias="pt_contract_type_name")
    created_at: Series[String] = pa.Field(coerce=True, nullable=False, description="", alias="created_at")
    updated_at: Series[String] = pa.Field(coerce=True, nullable=False, description="", alias="updated_at")

    class _Annotation:
        primary_key = "id"
        foreign_keys = {
            "employee_id": {
                "parent_schema": "EmployeesGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "es_contract_type_id": {
                "parent_schema": "Spanish_contract_typesGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "es_education_level_id": {
                "parent_schema": "Spanish_education_levelsGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "es_professional_category_id": {
                "parent_schema": "Spanish_professional_categoriesGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "fr_level_id": {
                "parent_schema": "French_levelSchema",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "fr_step_id": {
                "parent_schema": "French_stepSchema",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "fr_mutual_id": {
                "parent_schema": "French_mutualSchema",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "fr_professional_category_id": {
                "parent_schema": "French_professional_categoriesGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "fr_work_type_id": {
                "parent_schema": "French_work_typesGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "fr_contract_type_id": {
                "parent_schema": "French_contract_typesGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "de_contract_type_id": {
                "parent_schema": "German_contract_typesGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "pt_contract_type_id": {
                "parent_schema": "Portuguese_contract_typesGet",
                "parent_column": "id",
                "cardinality": "N:1"
            }
        }

class New_hiresGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="The id of the new hire incidence", alias="id")
    status: Series[String] = pa.Field(coerce=True, nullable=False, description="The status of the new hire incidence", alias="status")
    employee_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="The employee id of the new hire", alias="employee_id")
    first_name: Series[String] = pa.Field(coerce=True, nullable=False, description="name of the employee.", alias="first_name")
    last_name: Series[String] = pa.Field(coerce=True, nullable=False, description="last name of the employee.", alias="last_name")
    birth_name: Series[String] = pa.Field(coerce=True, nullable=True, description="The birth name of the new hire", alias="birth_name")
    identifier: Series[String] = pa.Field(coerce=True, nullable=True, description="national identifier number.", alias="identifier")
    identifier_type: Series[String] = pa.Field(coerce=True, nullable=True, description="type of identifier (ex passport).", alias="identifier_type")
    payroll_identifier: Series[String] = pa.Field(coerce=True, nullable=True, description="payroll identifier.", alias="payroll_identifier")
    work_email: Series[String] = pa.Field(coerce=True, nullable=True, description="personal email of the employee.", alias="work_email")
    phone_number: Series[String] = pa.Field(coerce=True, nullable=True, description="phone number of the employee.", alias="phone_number")
    gender: Series[String] = pa.Field(coerce=True, nullable=True, description="gender of the employee (male | female).", alias="gender")
    job_title: Series[String] = pa.Field(coerce=True, nullable=True, description="job title of the employee.", alias="job_title")
    address: Series[String] = pa.Field(coerce=True, nullable=False, description="address of the employee.", alias="address")
    city: Series[String] = pa.Field(coerce=True, nullable=True, description="city of the employee.", alias="city")
    country: Series[String] = pa.Field(coerce=True, nullable=True, description="country code of the employee (Spain ES, United Kingdom GB).", alias="country")
    state: Series[String] = pa.Field(coerce=True, nullable=True, description="state/province/region of the employee.", alias="state")
    postal_code: Series[String] = pa.Field(coerce=True, nullable=True, description="postal code of the employee.", alias="postal_code")
    date_of_birth: Series[String] = pa.Field(coerce=True, nullable=True, description="birthday of the employee.", alias="date_of_birth")
    nationality: Series[String] = pa.Field(coerce=True, nullable=True, description="nationality country code of the employee (Spain ES, United Kingdom GB).", alias="nationality")
    start_date: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="start_date")
    contract_effective_date: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="contract_effective_date")
    contract_end_date: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="contract_end_date")
    bank_account: Series[String] = pa.Field(coerce=True, nullable=True, description="bank account number of the employee.", alias="bank_account")
    salary_amount_in_cents: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="salary amount in cents.", alias="salary_amount_in_cents")
    salary_frequency: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="salary_frequency")
    working_hours: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="", alias="working_hours")
    working_hours_frequency: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="working_hours_frequency")
    social_security_number: Series[String] = pa.Field(coerce=True, nullable=True, description="social security number of the employee.", alias="social_security_number")
    manager_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="manager id of the employee, you can get the manager id from employees endpoint.", alias="manager_id")
    tax_id: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="tax_id")
    legal_entity_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="The legal entity id of the new hire", alias="legal_entity_id")
    workplace_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="workplace id of the employee.", alias="workplace_id")

    class _Annotation:
        primary_key = "id"
        foreign_keys = {
            "employee_id": {
                "parent_schema": "EmployeesGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "manager_id": {
                "parent_schema": "EmployeesGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "legal_entity_id": {
                "parent_schema": "Legal_entitiesGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "workplace_id": {
                "parent_schema": "LocationsGet",
                "parent_column": "id",
                "cardinality": "N:1"
            }
        }

class Personal_changesGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="The id of the new hire incidence", alias="id")
    status: Series[String] = pa.Field(coerce=True, nullable=False, description="The status of the new hire incidence", alias="status")
    employee_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="The employee id of the new hire", alias="employee_id")
    work_email: Series[String] = pa.Field(coerce=True, nullable=True, description="personal email of the employee.", alias="work_email")
    phone_number: Series[String] = pa.Field(coerce=True, nullable=True, description="phone number of the employee.", alias="phone_number")
    identifier_type: Series[String] = pa.Field(coerce=True, nullable=True, description="type of identifier (ex passport).", alias="identifier_type")
    identifier: Series[String] = pa.Field(coerce=True, nullable=True, description="national identifier number.", alias="identifier")
    social_security_number: Series[String] = pa.Field(coerce=True, nullable=True, description="social security number of the employee.", alias="social_security_number")
    tax_id: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="tax_id")
    first_name: Series[String] = pa.Field(coerce=True, nullable=False, description="name of the employee.", alias="first_name")
    last_name: Series[String] = pa.Field(coerce=True, nullable=False, description="last name of the employee.", alias="last_name")
    gender: Series[String] = pa.Field(coerce=True, nullable=True, description="gender of the employee (male | female).", alias="gender")
    date_of_birth: Series[String] = pa.Field(coerce=True, nullable=True, description="birthday of the employee.", alias="date_of_birth")
    nationality: Series[String] = pa.Field(coerce=True, nullable=True, description="nationality country code of the employee (Spain ES, United Kingdom GB).", alias="nationality")
    address_line_1: Series[String] = pa.Field(coerce=True, nullable=True, description="address line 1 of the employee.", alias="address_line_1")
    address_line_2: Series[String] = pa.Field(coerce=True, nullable=True, description="address line 1 of the employee.", alias="address_line_2")
    postal_code: Series[String] = pa.Field(coerce=True, nullable=True, description="postal code of the employee.", alias="postal_code")
    city: Series[String] = pa.Field(coerce=True, nullable=True, description="city of the employee.", alias="city")
    state: Series[String] = pa.Field(coerce=True, nullable=True, description="state/province/region of the employee.", alias="state")
    country: Series[String] = pa.Field(coerce=True, nullable=True, description="country code of the employee (Spain ES, United Kingdom GB).", alias="country")
    bank_number: Series[String] = pa.Field(coerce=True, nullable=True, description="bank account number of the employee.", alias="bank_number")
    job_title: Series[String] = pa.Field(coerce=True, nullable=True, description="job title of the employee.", alias="job_title")
    workplace_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="workplace id of the employee.", alias="workplace_id")

    class _Annotation:
        primary_key = "id"
        foreign_keys = {
            "employee_id": {
                "parent_schema": "EmployeesGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "workplace_id": {
                "parent_schema": "LocationsGet",
                "parent_column": "id",
                "cardinality": "N:1"
            }
        }

class TerminationsGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="", alias="id")
    status: Series[String] = pa.Field(coerce=True, nullable=False, description="", alias="status")
    employee_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="", alias="employee_id")
    terminated_on: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="terminated_on")
    termination_reason: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="termination_reason")
    termination_observations: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="termination_observations")
    legal_entity_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="", alias="legal_entity_id")
    remaining_holidays: Series[String] = pa.Field(coerce=True, nullable=False, description="", alias="remaining_holidays")
    termination_reason_type: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="termination_reason_type")
    termination_type_description: Series[String] = pa.Field(coerce=True, nullable=True, description="The description of the termination type.", alias="termination_type_description")

    class _Annotation:
        primary_key = "id"
        foreign_keys = {
            "employee_id": {
                "parent_schema": "EmployeesGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "legal_entity_id": {
                "parent_schema": "Legal_entitiesGet",
                "parent_column": "id",
                "cardinality": "N:1"
            }
        }

class AbsencesDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

class Contract_changesDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

class New_hiresDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

class Personal_changesDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

class SummariesDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

class TerminationsDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")
