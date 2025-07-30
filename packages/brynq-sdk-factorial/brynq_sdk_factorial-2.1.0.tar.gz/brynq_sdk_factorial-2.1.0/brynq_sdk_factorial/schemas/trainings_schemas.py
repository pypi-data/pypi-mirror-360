# Auto-generated schemas for category: trainings

import pandas as pd
import pandera as pa
from pandera.typing import Series, String, Int, Float, Bool, DateTime
import pandera.extensions as extensions
from brynq_sdk_functions import BrynQPanderaDataFrameModel
from typing import Optional, Annotated
from pydantic import BaseModel, Field, StringConstraints

class CategoriesGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="", alias="id")
    name: Series[String] = pa.Field(coerce=True, nullable=False, description="", alias="name")
    company_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="", alias="company_id")
    created_at: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="created_at")
    updated_at: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="updated_at")

class Session_access_membershipsGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="", alias="id")
    access_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="", alias="access_id")
    employee_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="", alias="employee_id")
    session_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="", alias="session_id")
    first_name: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="first_name")
    last_name: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="last_name")
    job_title: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="job_title")
    session_attendance_status: Series[String] = pa.Field(coerce=True, nullable=False, description="", alias="session_attendance_status")
    team_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="", alias="team_id")

class Session_attendancesGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="", alias="id")
    status: Series[String] = pa.Field(coerce=True, nullable=False, description="", alias="status")
    session_access_membership_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="", alias="session_access_membership_id")
    access_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="", alias="access_id")
    employee_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="", alias="employee_id")

class SessionsGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="", alias="id")
    name: Series[String] = pa.Field(coerce=True, nullable=False, description="", alias="name")
    training_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="", alias="training_id")
    description: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="description")
    training_class_id: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="training_class_id")
    starts_at: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="starts_at")
    ends_at: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="ends_at")
    due_date: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="due_date")
    duration: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="duration")
    modality: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="modality")
    link: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="link")
    location: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="location")
    session_attendance_ids: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="session_attendance_ids")
    session_feedback_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="", alias="session_feedback_id")
    subsidized: Series[Bool] = pa.Field(coerce=True, nullable=False, description="", alias="subsidized")
    status: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="status")
    session_attendances_status: Series[String] = pa.Field(coerce=True, nullable=False, description="", alias="session_attendances_status")

class Training_membershipsGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Unique identifier for the training membership.", alias="id")
    access_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Access_id associated to the employee, refers to employees/employees endpoint.", alias="access_id")
    training_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="This field is used to filter those trainings memberships that belongs to this training.", alias="training_id")
    status: Series[String] = pa.Field(coerce=True, nullable=False, description="This field is used to filter those trainings memberships whose attendance status is the given.", alias="status")
    training_due_date: Series[String] = pa.Field(coerce=True, nullable=True, description="This field is used for those trainings with an expiry date.", alias="training_due_date")
    training_completed_at: Series[String] = pa.Field(coerce=True, nullable=True, description="This field is used to record the date a training was completed for trainings that have an expiry date.", alias="training_completed_at")

class TrainingsGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Identifier of the course", alias="id")
    company_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Company identifier", alias="company_id")
    author_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="The person that creates the training", alias="author_id")
    name: Series[String] = pa.Field(coerce=True, nullable=False, description="Name of the training", alias="name")
    code: Series[String] = pa.Field(coerce=True, nullable=True, description="Code of the training", alias="code")
    description: Series[String] = pa.Field(coerce=True, nullable=False, description="Description of the training", alias="description")
    created_at: Series[String] = pa.Field(coerce=True, nullable=True, description="Creation date of the course", alias="created_at")
    updated_at: Series[String] = pa.Field(coerce=True, nullable=True, description="Last modification date of the course", alias="updated_at")
    external_provider: Series[String] = pa.Field(coerce=True, nullable=True, description="The name of the provider if any", alias="external_provider")
    external: Series[Bool] = pa.Field(coerce=True, nullable=False, description="External training", alias="external")
    total_cost: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="", alias="total_cost")
    fundae_subsidized: Series[Bool] = pa.Field(coerce=True, nullable=False, description="Subsidized by Fundae", alias="fundae_subsidized")
    subsidized: Series[Bool] = pa.Field(coerce=True, nullable=False, description="Marked as subsidized", alias="subsidized")
    cost: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="", alias="cost")
    subsidized_cost: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="", alias="subsidized_cost")
    total_cost_decimal: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="total_cost_decimal")
    cost_decimal: Series[String] = pa.Field(coerce=True, nullable=False, description="", alias="cost_decimal")
    subsidized_cost_decimal: Series[String] = pa.Field(coerce=True, nullable=False, description="", alias="subsidized_cost_decimal")
    category_ids: Series[String] = pa.Field(coerce=True, nullable=True, description="List of ids of training categories", alias="category_ids")
    status: Series[String] = pa.Field(coerce=True, nullable=True, description="Training status. Can be one of the following values", alias="status")
    year: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Year of the training", alias="year")
    catalog: Series[Bool] = pa.Field(coerce=True, nullable=False, description="Visible in catalog", alias="catalog")
    competency_ids: Series[String] = pa.Field(coerce=True, nullable=False, description="List of ids of training competencies", alias="competency_ids")
    total_training_cost: Series[String] = pa.Field(coerce=True, nullable=False, description="The total direct cost of all course's groups", alias="total_training_cost")
    total_training_indirect_cost: Series[String] = pa.Field(coerce=True, nullable=False, description="The total indirect cost of all course's groups", alias="total_training_indirect_cost")
    total_training_salary_cost: Series[String] = pa.Field(coerce=True, nullable=False, description="The total salary cost of all course's groups", alias="total_training_salary_cost")
    total_training_subsidized_cost: Series[String] = pa.Field(coerce=True, nullable=False, description="The total subsidized cost of all course's groups", alias="total_training_subsidized_cost")
    total_participants: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Number of participants of all course's groups", alias="total_participants")
    training_attendance_status: Series[String] = pa.Field(coerce=True, nullable=False, description="", alias="training_attendance_status")
    valid_for: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="Number of years this course is valid for", alias="valid_for")
    objectives: Series[String] = pa.Field(coerce=True, nullable=True, description="Objectives of the course", alias="objectives")
    number_of_expired_participants: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="Number of participants that have the course expired or about to expire in the next 3 months. Only applicable to trainings with validity period.", alias="number_of_expired_participants")

class CategoriesCreate(BaseModel):
    name: str = Field(..., description="", alias="name")
    company_id: int = Field(..., description="", alias="company_id")

class CategoriesDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

class Session_access_membershipsDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

class Session_attendancesDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

class SessionsCreate(BaseModel):
    name: str = Field(..., description="", alias="name")
    training_id: int = Field(..., description="", alias="training_id")
    description: Optional[str] = Field(None, description="", alias="description")
    training_class_id: Optional[int] = Field(None, description="", alias="training_class_id")
    starts_at: Optional[str] = Field(None, description="", alias="starts_at")
    ends_at: Optional[str] = Field(None, description="", alias="ends_at")
    due_date: Optional[str] = Field(None, description="", alias="due_date")
    duration: Optional[str] = Field(None, description="", alias="duration")
    modality: Optional[Annotated[str, StringConstraints(pattern=r'^online|inperson|mixed$', strip_whitespace=True)]] = Field(None, description="", alias="modality")
    link: Optional[str] = Field(None, description="", alias="link")
    location: Optional[str] = Field(None, description="", alias="location")
    subsidized: Optional[bool] = Field(None, description="", alias="subsidized")
    recurrent: Optional[bool] = Field(None, description="", alias="recurrent")
    reminders: Optional[str] = Field(None, description="", alias="reminders")

class SessionsUpdate(BaseModel):
    id: int = Field(..., description="ID", alias="id")
    name: str = Field(..., description="", alias="name")
    training_id: int = Field(..., description="", alias="training_id")
    description: Optional[str] = Field(None, description="", alias="description")
    training_class_id: Optional[str] = Field(None, description="", alias="training_class_id")
    starts_at: Optional[str] = Field(None, description="", alias="starts_at")
    ends_at: Optional[str] = Field(None, description="", alias="ends_at")
    due_date: Optional[str] = Field(None, description="", alias="due_date")
    duration: Optional[str] = Field(None, description="", alias="duration")
    modality: Optional[Annotated[str, StringConstraints(pattern=r'^online|inperson|mixed$', strip_whitespace=True)]] = Field(None, description="", alias="modality")
    link: Optional[str] = Field(None, description="", alias="link")
    location: Optional[str] = Field(None, description="", alias="location")
    session_attendance_ids: Optional[str] = Field(None, description="", alias="session_attendance_ids")
    session_feedback_id: Optional[int] = Field(None, description="", alias="session_feedback_id")
    subsidized: bool = Field(..., description="", alias="subsidized")
    status: Optional[str] = Field(None, description="", alias="status")
    session_attendances_status: str = Field(..., description="", alias="session_attendances_status")

class SessionsDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

class Training_membershipsUpdate(BaseModel):
    id: int = Field(..., description="ID", alias="id")
    access_id: int = Field(..., description="Access_id associated to the employee, refers to employees/employees endpoint.", alias="access_id")
    training_id: int = Field(..., description="This field is used to filter those trainings memberships that belongs to this training.", alias="training_id")
    status: str = Field(..., description="This field is used to filter those trainings memberships whose attendance status is the given.", alias="status")
    training_due_date: Optional[str] = Field(None, description="This field is used for those trainings with an expiry date.", alias="training_due_date")
    training_completed_at: Optional[str] = Field(None, description="This field is used to record the date a training was completed for trainings that have an expiry date.", alias="training_completed_at")

class Training_membershipsDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

class TrainingsCreate(BaseModel):
    name: str = Field(..., description="Name of the training", alias="name")
    code: Optional[str] = Field(None, description="Code of the training", alias="code")
    description: str = Field(..., description="Description of the training", alias="description")
    external_provider: Optional[str] = Field(None, description="External provider of the training", alias="external_provider")
    external: bool = Field(..., description="External training", alias="external")
    category_ids: Optional[str] = Field(None, description="", alias="category_ids")
    competency_ids: Optional[str] = Field(None, description="Competency ids of the training", alias="competency_ids")
    author_id: Optional[int] = Field(None, description="The person that creates the training", alias="author_id")
    employee_id: Optional[int] = Field(None, description="", alias="employee_id")
    cost: Optional[int] = Field(None, description="", alias="cost")
    subsidized_cost: Optional[int] = Field(None, description="", alias="subsidized_cost")
    cost_decimal: Optional[str] = Field(None, description="", alias="cost_decimal")
    subsidized_cost_decimal: Optional[str] = Field(None, description="", alias="subsidized_cost_decimal")
    year: int = Field(..., description="Year of the training", alias="year")
    company_id: Optional[int] = Field(None, description="Company identifier of the training", alias="company_id")
    attachments: str = Field(..., description="Attachments of the training", alias="attachments")
    valid_for: Optional[int] = Field(None, description="The training validity period in years", alias="valid_for")
    objectives: Optional[str] = Field(None, description="Objectives of the course", alias="objectives")

class TrainingsUpdate(BaseModel):
    id: int = Field(..., description="ID", alias="id")
    company_id: int = Field(..., description="Company identifier", alias="company_id")
    author_id: int = Field(..., description="The person that creates the training", alias="author_id")
    name: str = Field(..., description="Name of the training", alias="name")
    code: Optional[str] = Field(None, description="Code of the training", alias="code")
    description: str = Field(..., description="Description of the training", alias="description")
    created_at: Optional[str] = Field(None, description="Creation date of the course", alias="created_at")
    updated_at: Optional[str] = Field(None, description="Last modification date of the course", alias="updated_at")
    external_provider: Optional[str] = Field(None, description="The name of the provider if any", alias="external_provider")
    external: bool = Field(..., description="External training", alias="external")
    total_cost: Optional[int] = Field(None, description="", alias="total_cost")
    fundae_subsidized: bool = Field(..., description="Subsidized by Fundae", alias="fundae_subsidized")
    subsidized: bool = Field(..., description="Marked as subsidized", alias="subsidized")
    cost: int = Field(..., description="", alias="cost")
    subsidized_cost: int = Field(..., description="", alias="subsidized_cost")
    total_cost_decimal: Optional[str] = Field(None, description="", alias="total_cost_decimal")
    cost_decimal: str = Field(..., description="", alias="cost_decimal")
    subsidized_cost_decimal: str = Field(..., description="", alias="subsidized_cost_decimal")
    category_ids: Optional[str] = Field(None, description="List of ids of training categories", alias="category_ids")
    status: Optional[Annotated[str, StringConstraints(pattern=r'^draft|active|deleted$', strip_whitespace=True)]] = Field(None, description="Training status. Can be one of the following values", alias="status")
    year: int = Field(..., description="Year of the training", alias="year")
    catalog: bool = Field(..., description="Visible in catalog", alias="catalog")
    competency_ids: str = Field(..., description="List of ids of training competencies", alias="competency_ids")
    total_training_cost: str = Field(..., description="The total direct cost of all course's groups", alias="total_training_cost")
    total_training_indirect_cost: str = Field(..., description="The total indirect cost of all course's groups", alias="total_training_indirect_cost")
    total_training_salary_cost: str = Field(..., description="The total salary cost of all course's groups", alias="total_training_salary_cost")
    total_training_subsidized_cost: str = Field(..., description="The total subsidized cost of all course's groups", alias="total_training_subsidized_cost")
    total_participants: int = Field(..., description="Number of participants of all course's groups", alias="total_participants")
    training_attendance_status: Annotated[str, StringConstraints(pattern=r'^notassigned|notstarted|missing|started|partiallycompleted|completed$', strip_whitespace=True)] = Field(..., description="", alias="training_attendance_status")
    valid_for: Optional[int] = Field(None, description="Number of years this course is valid for", alias="valid_for")
    objectives: Optional[str] = Field(None, description="Objectives of the course", alias="objectives")
    number_of_expired_participants: Optional[int] = Field(None, description="Number of participants that have the course expired or about to expire in the next 3 months. Only applicable to trainings with validity period.", alias="number_of_expired_participants")

class TrainingsDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

