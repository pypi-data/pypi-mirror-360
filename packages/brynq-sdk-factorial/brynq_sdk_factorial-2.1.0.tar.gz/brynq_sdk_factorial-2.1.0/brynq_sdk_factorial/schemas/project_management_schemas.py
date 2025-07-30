# Auto-generated schemas for category: project_management

import pandas as pd
import pandera as pa
from pandera.typing import Series, String, Int, Float, Bool, DateTime
import pandera.extensions as extensions
from brynq_sdk_functions import BrynQPanderaDataFrameModel
from typing import Optional, Annotated
from pydantic import BaseModel, Field, StringConstraints

class Expense_recordsGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="", alias="id")
    project_worker_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="", alias="project_worker_id")
    expense_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="", alias="expense_id")
    subproject_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="", alias="subproject_id")
    original_amount_currency: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="original_amount_currency")
    original_amount_cents: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="", alias="original_amount_cents")
    legal_entity_amount_currency: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="legal_entity_amount_currency")
    legal_entity_amount_cents: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="legal_entity_amount_cents")
    effective_on: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="effective_on")
    exchange_rate: Series[Float] = pa.Field(coerce=True, nullable=True, description="", alias="exchange_rate")
    status: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="status")

class Flexible_time_record_commentsGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="", alias="id")
    content: Series[String] = pa.Field(coerce=True, nullable=False, description="", alias="content")
    flexible_time_record_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="", alias="flexible_time_record_id")

class Flexible_time_recordsGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="", alias="id")
    date: Series[String] = pa.Field(coerce=True, nullable=False, description="", alias="date")
    imputed_minutes: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="", alias="imputed_minutes")
    project_worker_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="", alias="project_worker_id")
    subproject_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="", alias="subproject_id")

class Project_tasksGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="", alias="id")
    project_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="", alias="project_id")
    subproject_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="", alias="subproject_id")
    task_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="", alias="task_id")
    follow_up: Series[Bool] = pa.Field(coerce=True, nullable=False, description="", alias="follow_up")

class Project_workersGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="id of the project worker.", alias="id")
    project_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="id of the project.", alias="project_id")
    employee_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="id of the employee.", alias="employee_id")
    assigned: Series[Bool] = pa.Field(coerce=True, nullable=False, description="true if the employee is assigned to the project, false otherwise.", alias="assigned")
    inputed_minutes: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="total inmputed minutes of the employee in the project.", alias="inputed_minutes")
    labor_cost_cents: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="total project currency labor cost of the employee in the project.", alias="labor_cost_cents")
    company_labor_cost_cents: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="total company currency labor cost of the employee in the project.", alias="company_labor_cost_cents")
    spending_cost_cents: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="total spending cost of the employee in the project.", alias="spending_cost_cents")

class ProjectsGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="The id of the project", alias="id")
    name: Series[String] = pa.Field(coerce=True, nullable=False, description="The name of the project", alias="name")
    code: Series[String] = pa.Field(coerce=True, nullable=True, description="The code of the project", alias="code")
    start_date: Series[String] = pa.Field(coerce=True, nullable=True, description="The start date of the project", alias="start_date")
    due_date: Series[String] = pa.Field(coerce=True, nullable=True, description="The end date of the project", alias="due_date")
    status: Series[String] = pa.Field(coerce=True, nullable=False, description="The status of the project", alias="status")
    employees_assignment: Series[String] = pa.Field(coerce=True, nullable=False, description="The employees assigment of the project", alias="employees_assignment")
    inputed_minutes: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="", alias="inputed_minutes")
    is_billable: Series[Bool] = pa.Field(coerce=True, nullable=False, description="Check if the projects is billable", alias="is_billable")
    fixed_cost_cents: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="Total fixed costs in cents", alias="fixed_cost_cents")
    labor_cost_cents: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="Total labor costs in cents", alias="labor_cost_cents")
    legal_entity_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="The legal entity id of the project", alias="legal_entity_id")
    spending_cost_cents: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="Total spending costs in cents", alias="spending_cost_cents")
    client_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="The client id of the project", alias="client_id")
    total_cost_cents: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="Total Cost in cents", alias="total_cost_cents")

class SubprojectsGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="", alias="id")
    name: Series[String] = pa.Field(coerce=True, nullable=False, description="", alias="name")
    project_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="", alias="project_id")
    inputed_minutes: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="", alias="inputed_minutes")
    labor_cost_cents: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="", alias="labor_cost_cents")

class Time_recordsGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Id of the time record", alias="id")
    project_worker_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Id of the project worker", alias="project_worker_id")
    attendance_shift_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Id of the attendance shift", alias="attendance_shift_id")
    subproject_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="Id of the subproject", alias="subproject_id")
    date: Series[String] = pa.Field(coerce=True, nullable=True, description="Reference date of the shift", alias="date")
    imputed_minutes: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="Minutes difference between the clock in and clock out", alias="imputed_minutes")
    clock_in: Series[String] = pa.Field(coerce=True, nullable=True, description="Clock in time", alias="clock_in")
    clock_out: Series[String] = pa.Field(coerce=True, nullable=True, description="Clock out time", alias="clock_out")

class Expense_recordsDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

class Flexible_time_record_commentsCreate(BaseModel):
    content: str = Field(..., description="", alias="content")
    flexible_time_record_id: int = Field(..., description="", alias="flexible_time_record_id")

class Flexible_time_record_commentsDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

class Flexible_time_recordsCreate(BaseModel):
    project_worker_id: int = Field(..., description="", alias="project_worker_id")
    date: str = Field(..., description="", alias="date")
    imputed_minutes: int = Field(..., description="", alias="imputed_minutes")
    subproject_id: Optional[int] = Field(None, description="", alias="subproject_id")

class Flexible_time_recordsUpdate(BaseModel):
    id: int = Field(..., description="ID", alias="id")
    date: str = Field(..., description="", alias="date")
    imputed_minutes: int = Field(..., description="", alias="imputed_minutes")
    project_worker_id: int = Field(..., description="", alias="project_worker_id")
    subproject_id: Optional[int] = Field(None, description="", alias="subproject_id")

class Flexible_time_recordsDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

class Project_tasksCreate(BaseModel):
    name: str = Field(..., description="", alias="name")
    content: Optional[str] = Field(None, description="", alias="content")
    starts_on: Optional[str] = Field(None, description="", alias="starts_on")
    follow_up: Optional[bool] = Field(None, description="", alias="follow_up")
    due_on: Optional[str] = Field(None, description="", alias="due_on")
    assignee_ids: Optional[str] = Field(None, description="", alias="assignee_ids")
    project_id: int = Field(..., description="", alias="project_id")
    subproject_id: Optional[int] = Field(None, description="", alias="subproject_id")
    files: Optional[str] = Field(None, description="", alias="files")
    status: Annotated[str, StringConstraints(pattern=r'^todo|in_progress|done|discarded$', strip_whitespace=True)] = Field(..., description="", alias="status")

class Project_tasksUpdate(BaseModel):
    id: int = Field(..., description="ID", alias="id")
    project_id: int = Field(..., description="", alias="project_id")
    subproject_id: Optional[int] = Field(None, description="", alias="subproject_id")
    task_id: int = Field(..., description="", alias="task_id")
    follow_up: bool = Field(..., description="", alias="follow_up")

class Project_tasksDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

class Project_workersCreate(BaseModel):
    project_id: int = Field(..., description="The id of the project to assign the employee project worker.", alias="project_id")
    employee_id: int = Field(..., description="The id of the employee to be assigned to the project.", alias="employee_id")

class Project_workersDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

class ProjectsCreate(BaseModel):
    name: str = Field(..., description="Mandatory to pass a name of the project.", alias="name")
    code: Optional[str] = Field(None, description="Optional unique code for the project to be identifiable and searchable.", alias="code")
    start_date: Optional[str] = Field(None, description="Optional start date for the project. If given must be in iso-8601 format (YYYY-MM-DD).", alias="start_date")
    due_date: Optional[str] = Field(None, description="Optional due date for the project. If given must be in iso-8601 format (YYYY-MM-DD).", alias="due_date")
    status: Optional[str] = Field(None, description="Project status. Can be `active` or `closed`", alias="status")
    employees_assignment: Optional[str] = Field(None, description="Optional param to define the kind of assignation the project has. Can be `manual` or `company`", alias="employees_assignment")
    project_admins: Optional[str] = Field(None, description="", alias="project_admins")
    project_managers: Optional[str] = Field(None, description="", alias="project_managers")
    is_billable: Optional[bool] = Field(None, description="", alias="is_billable")
    fixed_cost_cents: Optional[int] = Field(None, description="", alias="fixed_cost_cents")
    budget_allocation: Optional[int] = Field(None, description="", alias="budget_allocation")
    legal_entity_id: Optional[int] = Field(None, description="", alias="legal_entity_id")
    budget_allocation_cents: Optional[int] = Field(None, description="", alias="budget_allocation_cents")
    fee_amount_cents: Optional[int] = Field(None, description="", alias="fee_amount_cents")

class ProjectsUpdate(BaseModel):
    id: int = Field(..., description="ID", alias="id")
    name: str = Field(..., description="The name of the project", alias="name")
    code: Optional[str] = Field(None, description="The code of the project", alias="code")
    start_date: Optional[str] = Field(None, description="The start date of the project", alias="start_date")
    due_date: Optional[str] = Field(None, description="The end date of the project", alias="due_date")
    status: Annotated[str, StringConstraints(pattern=r'^active|closed|draft|processing$', strip_whitespace=True)] = Field(..., description="The status of the project", alias="status")
    employees_assignment: Annotated[str, StringConstraints(pattern=r'^manual|company$', strip_whitespace=True)] = Field(..., description="The employees assigment of the project", alias="employees_assignment")
    inputed_minutes: Optional[int] = Field(None, description="", alias="inputed_minutes")
    is_billable: bool = Field(..., description="Check if the projects is billable", alias="is_billable")
    fixed_cost_cents: Optional[int] = Field(None, description="Total fixed costs in cents", alias="fixed_cost_cents")
    labor_cost_cents: Optional[int] = Field(None, description="Total labor costs in cents", alias="labor_cost_cents")
    legal_entity_id: int = Field(..., description="The legal entity id of the project", alias="legal_entity_id")
    spending_cost_cents: Optional[int] = Field(None, description="Total spending costs in cents", alias="spending_cost_cents")
    client_id: Optional[int] = Field(None, description="The client id of the project", alias="client_id")
    total_cost_cents: Optional[int] = Field(None, description="Total Cost in cents", alias="total_cost_cents")

class ProjectsDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

class SubprojectsCreate(BaseModel):
    name: str = Field(..., description="", alias="name")
    project_id: int = Field(..., description="", alias="project_id")

class SubprojectsDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

class Time_recordsCreate(BaseModel):
    project_worker_id: int = Field(..., description="", alias="project_worker_id")
    attendance_shift_id: int = Field(..., description="", alias="attendance_shift_id")
    subproject_id: Optional[int] = Field(None, description="", alias="subproject_id")

class Time_recordsDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

