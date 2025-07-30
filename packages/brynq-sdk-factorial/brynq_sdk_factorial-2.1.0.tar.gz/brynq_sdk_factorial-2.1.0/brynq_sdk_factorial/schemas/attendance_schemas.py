# Auto-generated schemas for category: attendance

import pandas as pd
import pandera as pa
from pandera.typing import Series, String, Int, Float, Bool, DateTime
import pandera.extensions as extensions
from brynq_sdk_functions import BrynQPanderaDataFrameModel
from typing import Optional, Annotated
from pydantic import BaseModel, Field, StringConstraints

class Break_configurationsGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="", alias="id")
    attendance_employees_setting_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Id of the attendance employee setting", alias="attendance_employees_setting_id")
    time_settings_break_configuration_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Id of the time settings break configuration", alias="time_settings_break_configuration_id")
    enabled: Series[Bool] = pa.Field(coerce=True, nullable=False, description="Status of the break configuration if enabled or not", alias="enabled")
    name: Series[String] = pa.Field(coerce=True, nullable=True, description="Name of the break configuration", alias="name")
    paid: Series[Bool] = pa.Field(coerce=True, nullable=True, description="Check the break configuration is paid or not", alias="paid")

    class _Annotation:
        primary_key = "id"
        foreign_keys = {
            "time_settings_break_configuration_id": {
                "parent_schema": "Break_configurationsGet",
                "parent_column": "id",
                "cardinality": "N:1"
            }
        }

class Edit_timesheet_requestsGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Unique identifier for the edit timesheet request", alias="id")
    approved: Series[Bool] = pa.Field(coerce=True, nullable=True, description="Status of the edit timesheet request", alias="approved")
    request_type: Series[String] = pa.Field(coerce=True, nullable=False, description="Type of the request", alias="request_type")
    employee_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Id of the shift's employee", alias="employee_id")
    workable: Series[Bool] = pa.Field(coerce=True, nullable=True, description="Indicates if the shift is workable or a break", alias="workable")
    clock_in: Series[String] = pa.Field(coerce=True, nullable=True, description="Clock in of the shift", alias="clock_in")
    clock_out: Series[String] = pa.Field(coerce=True, nullable=True, description="Clock out of the shift", alias="clock_out")
    location_type: Series[String] = pa.Field(coerce=True, nullable=True, description="Location of the shift", alias="location_type")
    reason: Series[String] = pa.Field(coerce=True, nullable=True, description="Approve or reject reason", alias="reason")
    attendance_shift_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="Id of the shift for the request", alias="attendance_shift_id")
    time_settings_break_configuration_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="Id of the type of break for the request", alias="time_settings_break_configuration_id")
    observations: Series[String] = pa.Field(coerce=True, nullable=True, description="Additional observations for the shift", alias="observations")
    date: Series[String] = pa.Field(coerce=True, nullable=True, description="Date of the shift", alias="date")
    reference_date: Series[String] = pa.Field(coerce=True, nullable=True, description="Reference date for the shift", alias="reference_date")

    class _Annotation:
        primary_key = "id"
        foreign_keys = {
            "employee_id": {
                "parent_schema": "EmployeesGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "attendance_shift_id": {
                "parent_schema": "ShiftsGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "time_settings_break_configuration_id": {
                "parent_schema": "Break_configurationsGet",
                "parent_column": "id",
                "cardinality": "N:1"
            }
        }

class Overtime_requestsGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="", alias="id")
    employee_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="", alias="employee_id")
    approver_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="", alias="approver_id")
    author_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="", alias="author_id")
    status: Series[String] = pa.Field(coerce=True, nullable=False, description="", alias="status")
    description: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="description")
    reason: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="reason")
    date: Series[String] = pa.Field(coerce=True, nullable=False, description="", alias="date")
    hours_amount_in_cents: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="", alias="hours_amount_in_cents")
    created_at: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="created_at")
    approver: Series[Bool] = pa.Field(coerce=True, nullable=False, description="", alias="approver")
    approver_full_name: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="approver_full_name")
    is_editable: Series[Bool] = pa.Field(coerce=True, nullable=False, description="Defines if the overtime request can be edited", alias="is_editable")

    class _Annotation:
        primary_key = "id"
        foreign_keys = {
            "employee_id": {
                "parent_schema": "EmployeesGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "approver_id": {
                "parent_schema": "EmployeesGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "author_id": {
                "parent_schema": "EmployeesGet",
                "parent_column": "id",
                "cardinality": "N:1"
            }
        }

class ShiftsGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Unique identifier for the shift", alias="id")
    employee_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Identifier for the employee assigned to the shift", alias="employee_id")
    date: Series[String] = pa.Field(coerce=True, nullable=False, description="Date of the shift", alias="date")
    reference_date: Series[String] = pa.Field(coerce=True, nullable=False, description="Reference date for the shift", alias="reference_date")
    clock_in: Series[String] = pa.Field(coerce=True, nullable=True, description="Time when the employee clocked in", alias="clock_in")
    clock_out: Series[String] = pa.Field(coerce=True, nullable=True, description="Time when the employee clocked out", alias="clock_out")
    in_source: Series[String] = pa.Field(coerce=True, nullable=True, description="Source of the clock-in time", alias="in_source")
    out_source: Series[String] = pa.Field(coerce=True, nullable=True, description="Source of the clock-out time", alias="out_source")
    observations: Series[String] = pa.Field(coerce=True, nullable=True, description="Additional observations about the shift", alias="observations")
    location_type: Series[String] = pa.Field(coerce=True, nullable=True, description="Type of location for the shift", alias="location_type")
    half_day: Series[String] = pa.Field(coerce=True, nullable=True, description="Indicates which worked part of the day", alias="half_day")
    in_location_latitude: Series[Float] = pa.Field(coerce=True, nullable=True, description="Latitude of the clock-in location", alias="in_location_latitude")
    in_location_longitude: Series[Float] = pa.Field(coerce=True, nullable=True, description="Longitude of the clock-in location", alias="in_location_longitude")
    in_location_accuracy: Series[Float] = pa.Field(coerce=True, nullable=True, description="Accuracy of the clock-in location", alias="in_location_accuracy")
    out_location_latitude: Series[Float] = pa.Field(coerce=True, nullable=True, description="Latitude of the clock-out location", alias="out_location_latitude")
    out_location_longitude: Series[Float] = pa.Field(coerce=True, nullable=True, description="Longitude of the clock-out location", alias="out_location_longitude")
    out_location_accuracy: Series[Float] = pa.Field(coerce=True, nullable=True, description="Accuracy of the clock-out location", alias="out_location_accuracy")
    workable: Series[Bool] = pa.Field(coerce=True, nullable=True, description="Indicates if the shift is workable", alias="workable")
    created_at: Series[String] = pa.Field(coerce=True, nullable=False, description="Timestamp when the shift record was created", alias="created_at")
    workplace_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="Identifier for the location", alias="workplace_id")
    time_settings_break_configuration_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="Identifier for the break configuration", alias="time_settings_break_configuration_id")
    company_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Identifier for the company", alias="company_id")
    updated_at: Series[String] = pa.Field(coerce=True, nullable=False, description="Timestamp when the shift record was updated", alias="updated_at")
    minutes: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Number in minutes of the shift", alias="minutes")
    clock_in_with_seconds: Series[String] = pa.Field(coerce=True, nullable=True, description="Clock in time with seconds", alias="clock_in_with_seconds")

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
            },
            "time_settings_break_configuration_id": {
                "parent_schema": "Break_configurationsGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },

        }

class Break_configurationsCreate(BaseModel):
    time_settings_break_configuration_id: int = Field(..., description="Id of the time settings break configuration", alias="time_settings_break_configuration_id")
    attendance_employees_setting_id: int = Field(..., description="Id of the attendance employee setting", alias="attendance_employees_setting_id")
    enabled: bool = Field(..., description="Status of the break configuration if enabled or not", alias="enabled")

class Break_configurationsUpdate(BaseModel):
    id: int = Field(..., description="ID", alias="id")
    attendance_employees_setting_id: int = Field(..., description="Id of the attendance employee setting", alias="attendance_employees_setting_id")
    time_settings_break_configuration_id: int = Field(..., description="Id of the time settings break configuration", alias="time_settings_break_configuration_id")
    enabled: bool = Field(..., description="Status of the break configuration if enabled or not", alias="enabled")
    name: Optional[str] = Field(None, description="Name of the break configuration", alias="name")
    paid: Optional[bool] = Field(None, description="Check the break configuration is paid or not", alias="paid")

class Break_configurationsDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

class Edit_timesheet_requestsCreate(BaseModel):
    employee_id: int = Field(..., description="", alias="employee_id")
    request_type: Annotated[str, StringConstraints(pattern=r'^create_shift|delete_shift|update_shift$', strip_whitespace=True)] = Field(..., description="", alias="request_type")
    reason: Optional[str] = Field(None, description="", alias="reason")
    date: Optional[str] = Field(None, description="", alias="date")
    clock_in: Optional[str] = Field(None, description="", alias="clock_in")
    clock_out: Optional[str] = Field(None, description="", alias="clock_out")
    workable: Optional[bool] = Field(None, description="", alias="workable")
    attendance_shift_id: Optional[int] = Field(None, description="", alias="attendance_shift_id")
    reference_date: Optional[str] = Field(None, description="", alias="reference_date")
    time_settings_break_configuration_id: Optional[int] = Field(None, description="", alias="time_settings_break_configuration_id")
    location_type: Optional[Annotated[str, StringConstraints(pattern=r'^office|business_trip|work_from_home$', strip_whitespace=True)]] = Field(None, description="", alias="location_type")
    observations: Optional[str] = Field(None, description="", alias="observations")

class Edit_timesheet_requestsUpdate(BaseModel):
    id: int = Field(..., description="ID", alias="id")
    approved: Optional[bool] = Field(None, description="Status of the edit timesheet request", alias="approved")
    request_type: Annotated[str, StringConstraints(pattern=r'^create_shift|delete_shift|update_shift$', strip_whitespace=True)] = Field(..., description="Type of the request", alias="request_type")
    employee_id: int = Field(..., description="Id of the shift's employee", alias="employee_id")
    workable: Optional[bool] = Field(None, description="Indicates if the shift is workable or a break", alias="workable")
    clock_in: Optional[str] = Field(None, description="Clock in of the shift", alias="clock_in")
    clock_out: Optional[str] = Field(None, description="Clock out of the shift", alias="clock_out")
    location_type: Optional[Annotated[str, StringConstraints(pattern=r'^office|business_trip|work_from_home$', strip_whitespace=True)]] = Field(None, description="Location of the shift", alias="location_type")
    reason: Optional[str] = Field(None, description="Approve or reject reason", alias="reason")
    attendance_shift_id: Optional[int] = Field(None, description="Id of the shift for the request", alias="attendance_shift_id")
    time_settings_break_configuration_id: Optional[int] = Field(None, description="Id of the type of break for the request", alias="time_settings_break_configuration_id")
    observations: Optional[str] = Field(None, description="Additional observations for the shift", alias="observations")
    date: Optional[str] = Field(None, description="Date of the shift", alias="date")
    reference_date: Optional[str] = Field(None, description="Reference date for the shift", alias="reference_date")

class Edit_timesheet_requestsDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

class Overtime_requestsCreate(BaseModel):
    date: str = Field(..., description="", alias="date")
    description: Optional[str] = Field(None, description="", alias="description")
    hours_amount: Optional[float] = Field(None, description="", alias="hours_amount")
    employee_id: int = Field(..., description="", alias="employee_id")
    author_id: int = Field(..., description="", alias="author_id")

class Overtime_requestsUpdate(BaseModel):
    id: int = Field(..., description="ID", alias="id")
    employee_id: int = Field(..., description="", alias="employee_id")
    approver_id: Optional[int] = Field(None, description="", alias="approver_id")
    author_id: int = Field(..., description="", alias="author_id")
    status: Annotated[str, StringConstraints(pattern=r'^pending|approved|rejected|none$', strip_whitespace=True)] = Field(..., description="", alias="status")
    description: Optional[str] = Field(None, description="", alias="description")
    reason: Optional[str] = Field(None, description="", alias="reason")
    date: str = Field(..., description="", alias="date")
    hours_amount_in_cents: int = Field(..., description="", alias="hours_amount_in_cents")
    created_at: Optional[str] = Field(None, description="", alias="created_at")
    approver: bool = Field(..., description="", alias="approver")
    approver_full_name: Optional[str] = Field(None, description="", alias="approver_full_name")
    is_editable: bool = Field(..., description="Defines if the overtime request can be edited", alias="is_editable")

class Overtime_requestsDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

class ShiftsCreate(BaseModel):
    employee_id: Optional[int] = Field(None, description="Id of the employee related", alias="employee_id")
    date: str = Field(..., description="Date of the shift", alias="date")
    reference_date: Optional[str] = Field(None, description="Reference date of the shift", alias="reference_date")
    day: Optional[int] = Field(None, description="number of days of the shift", alias="day")
    clock_in: Optional[str] = Field(None, description="Time of the clock in", alias="clock_in")
    clock_out: Optional[str] = Field(None, description="Time of the clock out", alias="clock_out")
    observations: Optional[str] = Field(None, description="Comments added to the shift", alias="observations")
    half_day: Optional[str] = Field(None, description="Boolean that indicates if the shift is a half day", alias="half_day")
    workable: Optional[bool] = Field(None, description="Boolean that indicates if the shift is workable", alias="workable")
    location_type: Optional[Annotated[str, StringConstraints(pattern=r'^office|business_trip|work_from_home$', strip_whitespace=True)]] = Field(None, description="Type of the location", alias="location_type")
    source: Optional[Annotated[str, StringConstraints(pattern=r'^desktop|mobile|face_recognition|qr_code|mobile_geolocation|shared_device|api|system$', strip_whitespace=True)]] = Field(None, description="Source of the shift creation", alias="source")
    time_settings_break_configuration_id: Optional[int] = Field(None, description="Id of the break configuration", alias="time_settings_break_configuration_id")

class ShiftsUpdate(BaseModel):
    id: int = Field(..., description="ID", alias="id")
    employee_id: int = Field(..., description="Identifier for the employee assigned to the shift", alias="employee_id")
    date: str = Field(..., description="Date of the shift", alias="date")
    reference_date: str = Field(..., description="Reference date for the shift", alias="reference_date")
    clock_in: Optional[str] = Field(None, description="Time when the employee clocked in", alias="clock_in")
    clock_out: Optional[str] = Field(None, description="Time when the employee clocked out", alias="clock_out")
    in_source: Optional[str] = Field(None, description="Source of the clock-in time", alias="in_source")
    out_source: Optional[str] = Field(None, description="Source of the clock-out time", alias="out_source")
    observations: Optional[str] = Field(None, description="Additional observations about the shift", alias="observations")
    location_type: Optional[Annotated[str, StringConstraints(pattern=r'^office|business_trip|work_from_home$', strip_whitespace=True)]] = Field(None, description="Type of location for the shift", alias="location_type")
    half_day: Optional[Annotated[str, StringConstraints(pattern=r'^beginning_of_day|end_of_day$', strip_whitespace=True)]] = Field(None, description="Indicates which worked part of the day", alias="half_day")
    in_location_latitude: Optional[float] = Field(None, description="Latitude of the clock-in location", alias="in_location_latitude")
    in_location_longitude: Optional[float] = Field(None, description="Longitude of the clock-in location", alias="in_location_longitude")
    in_location_accuracy: Optional[float] = Field(None, description="Accuracy of the clock-in location", alias="in_location_accuracy")
    out_location_latitude: Optional[float] = Field(None, description="Latitude of the clock-out location", alias="out_location_latitude")
    out_location_longitude: Optional[float] = Field(None, description="Longitude of the clock-out location", alias="out_location_longitude")
    out_location_accuracy: Optional[float] = Field(None, description="Accuracy of the clock-out location", alias="out_location_accuracy")
    workable: Optional[bool] = Field(None, description="Indicates if the shift is workable", alias="workable")
    created_at: str = Field(..., description="Timestamp when the shift record was created", alias="created_at")
    workplace_id: Optional[int] = Field(None, description="Identifier for the location", alias="workplace_id")
    time_settings_break_configuration_id: Optional[int] = Field(None, description="Identifier for the break configuration", alias="time_settings_break_configuration_id")
    company_id: int = Field(..., description="Identifier for the company", alias="company_id")
    updated_at: str = Field(..., description="Timestamp when the shift record was updated", alias="updated_at")
    minutes: int = Field(..., description="Number in minutes of the shift", alias="minutes")
    clock_in_with_seconds: Optional[str] = Field(None, description="Clock in time with seconds", alias="clock_in_with_seconds")

class ShiftsDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")
