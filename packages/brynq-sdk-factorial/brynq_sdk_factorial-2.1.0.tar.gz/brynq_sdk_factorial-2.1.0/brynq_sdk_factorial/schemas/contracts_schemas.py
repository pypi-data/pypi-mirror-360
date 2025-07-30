# Auto-generated schemas for category: contracts

import pandas as pd
import pandera as pa
from pandera.typing import Series, String, Int, Float, Bool, DateTime
import pandera.extensions as extensions
from brynq_sdk_functions import BrynQPanderaDataFrameModel
from typing import Optional, Annotated
from pydantic import BaseModel, Field, StringConstraints

class CompensationsGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Compensation ID", alias="id")
    contract_version_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Contract version ID", alias="contract_version_id")
    contracts_taxonomy_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Contracts taxonomy ID", alias="contracts_taxonomy_id")
    description: Series[String] = pa.Field(coerce=True, nullable=True, description="Compensation description", alias="description")
    compensation_type: Series[String] = pa.Field(coerce=True, nullable=True, description="Required field. You can only use the following options: fixed, undefined, up_to, per_worked_day, per_worked_hour", alias="compensation_type")
    amount: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="Required field unless your compensation type is undefined", alias="amount")
    unit: Series[String] = pa.Field(coerce=True, nullable=False, description="Unit of the compensation", alias="unit")
    sync_with_supplements: Series[Bool] = pa.Field(coerce=True, nullable=True, description="Sync with supplements", alias="sync_with_supplements")
    payroll_policy_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="Payroll policy ID", alias="payroll_policy_id")
    recurrence_count: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="Recurrence count", alias="recurrence_count")
    starts_on: Series[String] = pa.Field(coerce=True, nullable=True, description="When the compensation starts_on", alias="starts_on")
    recurrence: Series[String] = pa.Field(coerce=True, nullable=True, description="Compensation recurrence", alias="recurrence")
    first_payment_on: Series[String] = pa.Field(coerce=True, nullable=True, description="When the first payment is done", alias="first_payment_on")
    calculation: Series[String] = pa.Field(coerce=True, nullable=True, description="Compensation calculation", alias="calculation")
    currency: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="currency")
    time_condition: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="time_condition")
    minimum_amount_of_hours: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="", alias="minimum_amount_of_hours")
    minimum_amount_of_hours_in_cents: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="Compensation expected minimum amount of hours in cents", alias="minimum_amount_of_hours_in_cents")

    class _Annotation:
        primary_key = "id"
        foreign_keys = {
            "contract_version_id": {
                "parent_schema": "Contract_versionsGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "contracts_taxonomy_id": {
                "parent_schema": "TaxonomiesGet",
                "parent_column": "id",
                "cardinality": "N:1"
            }
        }

class Contract_templatesGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Unique identifier for the contract template", alias="id")
    company_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="ID of the company this template belongs to", alias="company_id")
    contract_version_type: Series[String] = pa.Field(coerce=True, nullable=True, description="Type of contract version (e.g., es for Spain, fr for France)", alias="contract_version_type")

    class _Annotation:
        primary_key = "id"
        foreign_keys = {}

class Contract_versionsGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="identifier for the contract version.", alias="id")
    company_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="identifier for company.", alias="company_id")
    employee_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="employee identifier, refers to /employees/employees endpoint.", alias="employee_id")
    effective_on: Series[String] = pa.Field(coerce=True, nullable=False, description="the day the specific contract starts, in case of hiring the same than starts_on.", alias="effective_on")
    country: Series[String] = pa.Field(coerce=True, nullable=True, description="nationality country code of the employee (Spain ES, United Kingdom GB).", alias="country")
    job_title: Series[String] = pa.Field(coerce=True, nullable=True, description="job title of the employee.", alias="job_title")
    job_catalog_level_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="job catalog level identifier, refers to /job_catalog/levels endpoint.", alias="job_catalog_level_id")
    job_catalog_level: Series[String] = pa.Field(coerce=True, nullable=True, description="the level of the employee in the job catalog.", alias="job_catalog_level")
    job_catalog_role: Series[String] = pa.Field(coerce=True, nullable=True, description="the role of the employee in the job catalog.", alias="job_catalog_role")
    starts_on: Series[String] = pa.Field(coerce=True, nullable=True, description="the day the employee is hired.", alias="starts_on")
    ends_on: Series[String] = pa.Field(coerce=True, nullable=True, description="the day the employee is terminated.", alias="ends_on")
    has_payroll: Series[Bool] = pa.Field(coerce=True, nullable=False, description="boolean that indicates if the employee asociated to this contract belongs to a payroll policy.", alias="has_payroll")
    has_trial_period: Series[Bool] = pa.Field(coerce=True, nullable=True, description="a flag that indicates if the employee has a trial period.", alias="has_trial_period")
    trial_period_ends_on: Series[String] = pa.Field(coerce=True, nullable=True, description="when the trial period ends.", alias="trial_period_ends_on")
    salary_amount: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="the amount of money the employee earns.", alias="salary_amount")
    salary_frequency: Series[String] = pa.Field(coerce=True, nullable=True, description="the frequency of the salary payment.", alias="salary_frequency")
    working_week_days: Series[String] = pa.Field(coerce=True, nullable=True, description="the days of the week the employee works.", alias="working_week_days")
    working_hours: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="the amount of hours the employee works.", alias="working_hours")
    working_hours_frequency: Series[String] = pa.Field(coerce=True, nullable=True, description="the frequency of the working hours.", alias="working_hours_frequency")
    max_legal_yearly_hours: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="the maximum amount of hours the employee can work in a year.", alias="max_legal_yearly_hours")
    maximum_weekly_hours: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="the maximum amount of hours the employee can work in a week.", alias="maximum_weekly_hours")
    bank_holiday_treatment: Series[String] = pa.Field(coerce=True, nullable=False, description="Defines whether a bank holiday should be considered as a workable or non-workable day.", alias="bank_holiday_treatment")
    working_time_percentage_in_cents: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="Working time percentage in cents (e.g., when an employee is working part-time, the percentage of full-time hours they are working).", alias="working_time_percentage_in_cents")
    min_rest_minutes_between_days: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="the minimum amount of minutes the employee must rest between working periods.", alias="min_rest_minutes_between_days")
    max_work_minutes_per_day: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="the maximum amount of minutes the employee can work in a day.", alias="max_work_minutes_per_day")
    max_work_days_in_row: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="the maximum amount of days the employee can work in a row.", alias="max_work_days_in_row")
    min_rest_hours_in_row: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="the minimum amount of hours the employee must rest in a row.", alias="min_rest_hours_in_row")
    created_at: Series[String] = pa.Field(coerce=True, nullable=False, description="the date the contract version was created.", alias="created_at")
    updated_at: Series[String] = pa.Field(coerce=True, nullable=False, description="the date of the last contract version updated.", alias="updated_at")
    es_has_teleworking_contract: Series[Bool] = pa.Field(coerce=True, nullable=True, description="flag that indicates if the contract has teleworking.", alias="es_has_teleworking_contract")
    es_cotization_group: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="the group of cotization of the employee.", alias="es_cotization_group")
    contracts_es_tariff_group_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="the group of cotization of the employee.", alias="contracts_es_tariff_group_id")
    es_contract_observations: Series[String] = pa.Field(coerce=True, nullable=True, description="observations of the contract.", alias="es_contract_observations")
    es_job_description: Series[String] = pa.Field(coerce=True, nullable=True, description="the job description of the employee.", alias="es_job_description")
    es_contract_type_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="contract type identifier.", alias="es_contract_type_id")
    es_working_day_type_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="working day type identifier.", alias="es_working_day_type_id")
    es_education_level_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="education level identifier.", alias="es_education_level_id")
    es_professional_category_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="professional category identifier.", alias="es_professional_category_id")
    fr_employee_type: Series[String] = pa.Field(coerce=True, nullable=True, description="employee type.", alias="fr_employee_type")
    fr_forfait_jours: Series[Bool] = pa.Field(coerce=True, nullable=False, description="flag that indicates if the employee is allowed to work within the framework of a fixed number of days.", alias="fr_forfait_jours")
    fr_jours_par_an: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="the number of days the employee is allowed to work.", alias="fr_jours_par_an")
    fr_coefficient: Series[String] = pa.Field(coerce=True, nullable=True, description="coefficient for france contracts.", alias="fr_coefficient")
    fr_contract_type_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="contract type identifier.", alias="fr_contract_type_id")
    fr_level_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="level identifier.", alias="fr_level_id")
    fr_step_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="step identifier.", alias="fr_step_id")
    fr_mutual_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="mutual identifier.", alias="fr_mutual_id")
    fr_professional_category_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="professional category identifier.", alias="fr_professional_category_id")
    fr_work_type_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="work type identifier.", alias="fr_work_type_id")
    de_contract_type_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="contract type identifier.", alias="de_contract_type_id")
    pt_contract_type_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="contract type identifier.", alias="pt_contract_type_id")

    class _Annotation:
        primary_key = "id"
        foreign_keys = {
            "employee_id": {
                "parent_schema": "EmployeesGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "job_catalog_level_id": {
                "parent_schema": "LevelsGet",
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

class French_contract_typesGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="identifier for the contract type", alias="id")
    name: Series[String] = pa.Field(coerce=True, nullable=False, description="Contract type name", alias="name")

    class _Annotation:
        primary_key = "id"
        foreign_keys = {}

class German_contract_typesGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="identifier for the contract type", alias="id")
    name: Series[String] = pa.Field(coerce=True, nullable=False, description="Contract type name", alias="name")

    class _Annotation:
        primary_key = "id"
        foreign_keys = {}

class Portuguese_contract_typesGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="identifier for the contract type", alias="id")
    name: Series[String] = pa.Field(coerce=True, nullable=False, description="Contract type name", alias="name")

    class _Annotation:
        primary_key = "id"
        foreign_keys = {}

class Spanish_contract_typesGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="identifier for the contract type", alias="id")
    name: Series[String] = pa.Field(coerce=True, nullable=False, description="The name of the contract type", alias="name")
    default: Series[Bool] = pa.Field(coerce=True, nullable=True, description="This contract type is a predefined one", alias="default")
    contracts_contract_template_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="The contract template identifier. Refers to contracts/contract_templates.", alias="contracts_contract_template_id")

    class _Annotation:
        primary_key = "id"
        foreign_keys = {
            "contracts_contract_template_id": {
                "parent_schema": "Contract_templatesGet",
                "parent_column": "id",
                "cardinality": "N:1"
            }
        }

class Spanish_education_levelsGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Education level identifier", alias="id")
    name: Series[String] = pa.Field(coerce=True, nullable=False, description="education level name", alias="name")
    default: Series[Bool] = pa.Field(coerce=True, nullable=True, description="Whether the education level is a predefined value", alias="default")
    contracts_contract_template_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Contract template identifier, refers to contracts/contract_templates", alias="contracts_contract_template_id")

    class _Annotation:
        primary_key = "id"
        foreign_keys = {
            "contracts_contract_template_id": {
                "parent_schema": "Contract_templatesGet",
                "parent_column": "id",
                "cardinality": "N:1"
            }
        }

class Spanish_professional_categoriesGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Professional category identifier", alias="id")
    name: Series[String] = pa.Field(coerce=True, nullable=False, description="Professional category name", alias="name")
    default: Series[Bool] = pa.Field(coerce=True, nullable=True, description="Whether the professional category is a predefined value", alias="default")
    contracts_contract_template_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Contract template identifier, refers to contracts/contract_templates", alias="contracts_contract_template_id")

    class _Annotation:
        primary_key = "id"
        foreign_keys = {
            "contracts_contract_template_id": {
                "parent_schema": "Contract_templatesGet",
                "parent_column": "id",
                "cardinality": "N:1"
            }
        }

class TaxonomiesGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="", alias="id")
    name: Series[String] = pa.Field(coerce=True, nullable=False, description="", alias="name")
    archived: Series[Bool] = pa.Field(coerce=True, nullable=False, description="", alias="archived")
    default: Series[Bool] = pa.Field(coerce=True, nullable=False, description="", alias="default")
    legal_entity_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="", alias="legal_entity_id")

    class _Annotation:
        primary_key = "id"
        foreign_keys = {
            "legal_entity_id": {
                "parent_schema": "Legal_entitiesGet",
                "parent_column": "id",
                "cardinality": "N:1"
            }
        }

class CompensationsCreate(BaseModel):
    contract_version_id: int = Field(..., description="", alias="contract_version_id")
    contracts_taxonomy_id: int = Field(..., description="", alias="contracts_taxonomy_id")
    description: Optional[str] = Field(None, description="", alias="description")
    compensation_type: Optional[str] = Field(None, description="", alias="compensation_type")
    amount: Optional[int] = Field(None, description="", alias="amount")
    unit: Optional[str] = Field(None, description="", alias="unit")
    sync_with_supplements: Optional[bool] = Field(None, description="", alias="sync_with_supplements")
    payroll_policy_id: Optional[int] = Field(None, description="", alias="payroll_policy_id")
    recurrence_count: Optional[int] = Field(None, description="", alias="recurrence_count")
    starts_on: Optional[str] = Field(None, description="", alias="starts_on")
    recurrence: Optional[str] = Field(None, description="", alias="recurrence")
    first_payment_on: Optional[str] = Field(None, description="", alias="first_payment_on")
    calculation: Optional[str] = Field(None, description="", alias="calculation")
    time_condition: Optional[Annotated[str, StringConstraints(pattern=r'^full_day|half_day|custom$', strip_whitespace=True)]] = Field(None, description="", alias="time_condition")
    minimum_amount_of_hours: Optional[int] = Field(None, description="", alias="minimum_amount_of_hours")
    minimum_amount_of_hours_in_cents: Optional[int] = Field(None, description="", alias="minimum_amount_of_hours_in_cents")

class CompensationsUpdate(BaseModel):
    id: int = Field(..., description="ID", alias="id")
    contract_version_id: int = Field(..., description="Contract version ID", alias="contract_version_id")
    contracts_taxonomy_id: int = Field(..., description="Contracts taxonomy ID", alias="contracts_taxonomy_id")
    description: Optional[str] = Field(None, description="Compensation description", alias="description")
    compensation_type: Optional[str] = Field(None, description="Required field. You can only use the following options: fixed, undefined, up_to, per_worked_day, per_worked_hour", alias="compensation_type")
    amount: Optional[int] = Field(None, description="Required field unless your compensation type is undefined", alias="amount")
    unit: str = Field(..., description="Unit of the compensation", alias="unit")
    sync_with_supplements: Optional[bool] = Field(None, description="Sync with supplements", alias="sync_with_supplements")
    payroll_policy_id: Optional[int] = Field(None, description="Payroll policy ID", alias="payroll_policy_id")
    recurrence_count: Optional[int] = Field(None, description="Recurrence count", alias="recurrence_count")
    starts_on: Optional[str] = Field(None, description="When the compensation starts_on", alias="starts_on")
    recurrence: Optional[str] = Field(None, description="Compensation recurrence", alias="recurrence")
    first_payment_on: Optional[str] = Field(None, description="When the first payment is done", alias="first_payment_on")
    calculation: Optional[str] = Field(None, description="Compensation calculation", alias="calculation")
    currency: Optional[str] = Field(None, description="", alias="currency")
    time_condition: Optional[Annotated[str, StringConstraints(pattern=r'^full_day|half_day|custom$', strip_whitespace=True)]] = Field(None, description="", alias="time_condition")
    minimum_amount_of_hours: Optional[int] = Field(None, description="", alias="minimum_amount_of_hours")
    minimum_amount_of_hours_in_cents: Optional[int] = Field(None, description="Compensation expected minimum amount of hours in cents", alias="minimum_amount_of_hours_in_cents")

class CompensationsDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

class Contract_templatesDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

class Contract_versionsCreate(BaseModel):
    employee_id: int = Field(..., description="employee identifier, refers to /employees/employees endpoint.", alias="employee_id")
    effective_on: str = Field(..., description="the day the specific contract starts, in case of hiring the same than starts_on.", alias="effective_on")
    starts_on: str = Field(..., description="the day the employee is hired.", alias="starts_on")
    ends_on: Optional[str] = Field(None, description="the day the employee is terminated.", alias="ends_on")
    working_hours_frequency: Optional[str] = Field(None, description="the frequency of the working hours.", alias="working_hours_frequency")
    working_week_days: Optional[str] = Field(None, description="the days of the week the employee works.", alias="working_week_days")
    working_hours: Optional[int] = Field(None, description="the amount of hours the employee works.", alias="working_hours")
    max_legal_yearly_hours: Optional[int] = Field(None, description="the maximum amount of hours the employee can work in a year.", alias="max_legal_yearly_hours")
    maximum_weekly_hours: Optional[int] = Field(None, description="the maximum amount of hours the employee can work in a week.", alias="maximum_weekly_hours")
    min_rest_minutes_between_days: Optional[int] = Field(None, description="the minimum amount of minutes the employee must rest between working periods.", alias="min_rest_minutes_between_days")
    max_work_minutes_per_day: Optional[int] = Field(None, description="the maximum amount of minutes the employee can work in a day.", alias="max_work_minutes_per_day")
    max_work_days_in_row: Optional[int] = Field(None, description="the maximum amount of days the employee can work in a row.", alias="max_work_days_in_row")
    min_rest_hours_in_row: Optional[int] = Field(None, description="the minimum amount of hours the employee must rest in a row.", alias="min_rest_hours_in_row")
    salary_frequency: Optional[str] = Field(None, description="the frequency of the salary payment.", alias="salary_frequency")
    salary_amount: Optional[int] = Field(None, description="the amount of money the employee earns.", alias="salary_amount")
    job_title: Optional[str] = Field(None, description="job title of the employee.", alias="job_title")
    has_trial_period: Optional[bool] = Field(None, description="a flag that indicates if the employee has a trial period.", alias="has_trial_period")
    trial_period_ends_on: Optional[str] = Field(None, description="when the trial period ends.", alias="trial_period_ends_on")
    working_time_percentage_in_cents: Optional[int] = Field(None, description="Working time percentage in cents (e.g., when an employee is working part-time, the percentage of full-time hours they are working).", alias="working_time_percentage_in_cents")
    copy_current_contract_version: Optional[bool] = Field(None, description="wether to copy the current contract version.", alias="copy_current_contract_version")
    job_catalog_level_id: Optional[int] = Field(None, description="the id of the job catalog level.", alias="job_catalog_level_id")
    bank_holiday_treatment: Optional[Annotated[str, StringConstraints(pattern=r'^workable|non_workable$', strip_whitespace=True)]] = Field(None, description="Defines whether a bank holiday should be considered as a workable or non-workable day.", alias="bank_holiday_treatment")

class Contract_versionsUpdate(BaseModel):
    id: int = Field(..., description="ID", alias="id")
    company_id: int = Field(..., description="identifier for company.", alias="company_id")
    employee_id: int = Field(..., description="employee identifier, refers to /employees/employees endpoint.", alias="employee_id")
    effective_on: str = Field(..., description="the day the specific contract starts, in case of hiring the same than starts_on.", alias="effective_on")
    country: Optional[str] = Field(None, description="nationality country code of the employee (Spain ES, United Kingdom GB).", alias="country")
    job_title: Optional[str] = Field(None, description="job title of the employee.", alias="job_title")
    job_catalog_level_id: Optional[int] = Field(None, description="job catalog level identifier, refers to /job_catalog/levels endpoint.", alias="job_catalog_level_id")
    job_catalog_level: Optional[str] = Field(None, description="the level of the employee in the job catalog.", alias="job_catalog_level")
    job_catalog_role: Optional[str] = Field(None, description="the role of the employee in the job catalog.", alias="job_catalog_role")
    starts_on: Optional[str] = Field(None, description="the day the employee is hired.", alias="starts_on")
    ends_on: Optional[str] = Field(None, description="the day the employee is terminated.", alias="ends_on")
    has_payroll: bool = Field(..., description="boolean that indicates if the employee asociated to this contract belongs to a payroll policy.", alias="has_payroll")
    has_trial_period: Optional[bool] = Field(None, description="a flag that indicates if the employee has a trial period.", alias="has_trial_period")
    trial_period_ends_on: Optional[str] = Field(None, description="when the trial period ends.", alias="trial_period_ends_on")
    salary_amount: Optional[int] = Field(None, description="the amount of money the employee earns.", alias="salary_amount")
    salary_frequency: Optional[str] = Field(None, description="the frequency of the salary payment.", alias="salary_frequency")
    working_week_days: Optional[str] = Field(None, description="the days of the week the employee works.", alias="working_week_days")
    working_hours: Optional[int] = Field(None, description="the amount of hours the employee works.", alias="working_hours")
    working_hours_frequency: Optional[str] = Field(None, description="the frequency of the working hours.", alias="working_hours_frequency")
    max_legal_yearly_hours: Optional[int] = Field(None, description="the maximum amount of hours the employee can work in a year.", alias="max_legal_yearly_hours")
    maximum_weekly_hours: Optional[int] = Field(None, description="the maximum amount of hours the employee can work in a week.", alias="maximum_weekly_hours")
    bank_holiday_treatment: Annotated[str, StringConstraints(pattern=r'^workable|non_workable$', strip_whitespace=True)] = Field(..., description="Defines whether a bank holiday should be considered as a workable or non-workable day.", alias="bank_holiday_treatment")
    working_time_percentage_in_cents: Optional[int] = Field(None, description="Working time percentage in cents (e.g., when an employee is working part-time, the percentage of full-time hours they are working).", alias="working_time_percentage_in_cents")
    min_rest_minutes_between_days: Optional[int] = Field(None, description="the minimum amount of minutes the employee must rest between working periods.", alias="min_rest_minutes_between_days")
    max_work_minutes_per_day: Optional[int] = Field(None, description="the maximum amount of minutes the employee can work in a day.", alias="max_work_minutes_per_day")
    max_work_days_in_row: Optional[int] = Field(None, description="the maximum amount of days the employee can work in a row.", alias="max_work_days_in_row")
    min_rest_hours_in_row: Optional[int] = Field(None, description="the minimum amount of hours the employee must rest in a row.", alias="min_rest_hours_in_row")
    created_at: str = Field(..., description="the date the contract version was created.", alias="created_at")
    updated_at: str = Field(..., description="the date of the last contract version updated.", alias="updated_at")
    es_has_teleworking_contract: Optional[bool] = Field(None, description="flag that indicates if the contract has teleworking.", alias="es_has_teleworking_contract")
    es_cotization_group: Optional[int] = Field(None, description="the group of cotization of the employee.", alias="es_cotization_group")
    contracts_es_tariff_group_id: Optional[int] = Field(None, description="the group of cotization of the employee.", alias="contracts_es_tariff_group_id")
    es_contract_observations: Optional[str] = Field(None, description="observations of the contract.", alias="es_contract_observations")
    es_job_description: Optional[str] = Field(None, description="the job description of the employee.", alias="es_job_description")
    es_contract_type_id: Optional[int] = Field(None, description="contract type identifier.", alias="es_contract_type_id")
    es_working_day_type_id: Optional[int] = Field(None, description="working day type identifier.", alias="es_working_day_type_id")
    es_education_level_id: Optional[int] = Field(None, description="education level identifier.", alias="es_education_level_id")
    es_professional_category_id: Optional[int] = Field(None, description="professional category identifier.", alias="es_professional_category_id")
    fr_employee_type: Optional[str] = Field(None, description="employee type.", alias="fr_employee_type")
    fr_forfait_jours: bool = Field(..., description="flag that indicates if the employee is allowed to work within the framework of a fixed number of days.", alias="fr_forfait_jours")
    fr_jours_par_an: Optional[int] = Field(None, description="the number of days the employee is allowed to work.", alias="fr_jours_par_an")
    fr_coefficient: Optional[str] = Field(None, description="coefficient for france contracts.", alias="fr_coefficient")
    fr_contract_type_id: Optional[int] = Field(None, description="contract type identifier.", alias="fr_contract_type_id")
    fr_level_id: Optional[int] = Field(None, description="level identifier.", alias="fr_level_id")
    fr_step_id: Optional[int] = Field(None, description="step identifier.", alias="fr_step_id")
    fr_mutual_id: Optional[int] = Field(None, description="mutual identifier.", alias="fr_mutual_id")
    fr_professional_category_id: Optional[int] = Field(None, description="professional category identifier.", alias="fr_professional_category_id")
    fr_work_type_id: Optional[int] = Field(None, description="work type identifier.", alias="fr_work_type_id")
    de_contract_type_id: Optional[int] = Field(None, description="contract type identifier.", alias="de_contract_type_id")
    pt_contract_type_id: Optional[int] = Field(None, description="contract type identifier.", alias="pt_contract_type_id")

class Contract_versionsDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

class French_contract_typesDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

class German_contract_typesDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

class Portuguese_contract_typesDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

class Spanish_contract_typesCreate(BaseModel):
    name: str = Field(..., description="Contract type name", alias="name")
    contracts_contract_template_id: int = Field(..., description="Contract template identifier. Refers to contracts/contract_templates.", alias="contracts_contract_template_id")

class Spanish_contract_typesDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

class Spanish_education_levelsCreate(BaseModel):
    name: str = Field(..., description="Education level name", alias="name")
    contracts_contract_template_id: int = Field(..., description="Contract template identifier, refers to contracts/contract_templates", alias="contracts_contract_template_id")

class Spanish_education_levelsDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

class Spanish_professional_categoriesCreate(BaseModel):
    name: str = Field(..., description="Professional category name", alias="name")
    contracts_contract_template_id: int = Field(..., description="Contract template identifier, refers to contracts/contract_templates", alias="contracts_contract_template_id")

class Spanish_professional_categoriesDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

class TaxonomiesDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")
