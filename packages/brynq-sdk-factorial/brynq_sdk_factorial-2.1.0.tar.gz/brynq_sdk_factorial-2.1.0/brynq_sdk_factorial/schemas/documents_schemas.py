# Auto-generated schemas for category: documents

import pandas as pd
import pandera as pa
from pandera.typing import Series, String, Int, Float, Bool, DateTime
import pandera.extensions as extensions
from brynq_sdk_functions import BrynQPanderaDataFrameModel
from typing import Optional, Annotated
from pydantic import BaseModel, Field, StringConstraints

class DocumentsGet(BrynQPanderaDataFrameModel):
    author_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="access identifier of the author, refers to /employees/employees endpoint.", alias="author_id")
    company_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="company identifier, refers to /api/me endpoint.", alias="company_id")
    content_type: Series[String] = pa.Field(coerce=True, nullable=True, description="document content type.", alias="content_type")
    created_at: Series[String] = pa.Field(coerce=True, nullable=False, description="creation date of the document.", alias="created_at")
    employee_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="employee identifier associated to the document.", alias="employee_id")
    extension: Series[String] = pa.Field(coerce=True, nullable=True, description="document extension.", alias="extension")
    file_size: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="document file size in bytes.", alias="file_size")
    filename: Series[String] = pa.Field(coerce=True, nullable=False, description="name of the document.", alias="filename")
    folder_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="folder identifier, references to documents/folders endpoint.", alias="folder_id")
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="document identifier.", alias="id")
    is_company_document: Series[Bool] = pa.Field(coerce=True, nullable=True, description="flag that indicates if the document is a company document.", alias="is_company_document")
    is_management_document: Series[Bool] = pa.Field(coerce=True, nullable=True, description="flag that indicates if the document is a management document.", alias="is_management_document")
    is_pending_assignment: Series[Bool] = pa.Field(coerce=True, nullable=True, description="flag that indicates if the document is pending assignment.", alias="is_pending_assignment")
    leave_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="leave identifier associated to the document, refers to /timeoff/leaves endpoint.", alias="leave_id")
    public: Series[Bool] = pa.Field(coerce=True, nullable=False, description="flag to indicate if the document is public.", alias="public")
    signature_status: Series[String] = pa.Field(coerce=True, nullable=True, description="document signature status.", alias="signature_status")
    signees: Series[String] = pa.Field(coerce=True, nullable=True, description="list of signee access identifiers associated to the document, refers to /employees/employees endpoint.", alias="signees")
    space: Series[String] = pa.Field(coerce=True, nullable=False, description="document space.", alias="space")
    updated_at: Series[String] = pa.Field(coerce=True, nullable=False, description="last update date of the document.", alias="updated_at")
    deleted_at: Series[String] = pa.Field(coerce=True, nullable=True, description="deletion date of the document.", alias="deleted_at")

class FoldersGet(BrynQPanderaDataFrameModel):
    active: Series[Bool] = pa.Field(coerce=True, nullable=False, description="Whether the folder is active or not", alias="active")
    company_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="Company ID of the folder", alias="company_id")
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Folder ID", alias="id")
    name: Series[String] = pa.Field(coerce=True, nullable=False, description="Folder name", alias="name")
    parent_folder_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="Id of the parent folder", alias="parent_folder_id")
    space: Series[String] = pa.Field(coerce=True, nullable=False, description="The space of the folder is related to the place where the folder is displayed.", alias="space")

class DocumentsCreate(BaseModel):
    public: bool = Field(..., description="flag to indicate if the document is public.", alias="public")
    space: Annotated[str, StringConstraints(pattern=r'^employee_my_documents|company_public|company_internal|pending_to_assign|pending_to_destroy$', strip_whitespace=True)] = Field(..., description="document space, in case of employee_my_documents it's necessary to fill employee_id.", alias="space")
    folder_id: Optional[int] = Field(None, description="folder identifier, references to documents/folders endpoint.", alias="folder_id")
    file_filename: Optional[str] = Field(None, description="final name of the file, even if the file has been uploaded with a different name.", alias="file_filename")
    is_pending_assignment: bool = Field(..., description="flag that indicates if the document is pending assignment.", alias="is_pending_assignment")
    leave_id: Optional[int] = Field(None, description="leave identifier associated to the document, refers to /timeoff/leaves endpoint.", alias="leave_id")
    file: str = Field(..., description="file to upload, the binary file.", alias="file")
    employee_id: Optional[int] = Field(None, description="employee identifier associated to the document.", alias="employee_id")
    author_id: int = Field(..., description="access identifier of the author, refers to /employees/employees endpoint.", alias="author_id")
    company_id: int = Field(..., description="company identifier, refers to /api/me endpoint.", alias="company_id")
    signee_ids: str = Field(..., description="list of user access identifiers associated to the document, refers to /employees/employees endpoint.", alias="signee_ids")
    request_esignature: bool = Field(..., description="flag to indicate if the document requires an electronic signature.", alias="request_esignature")

class DocumentsUpdate(BaseModel):
    id: int = Field(..., description="ID", alias="id")
    author_id: Optional[int] = Field(None, description="access identifier of the author, refers to /employees/employees endpoint.", alias="author_id")
    company_id: Optional[int] = Field(None, description="company identifier, refers to /api/me endpoint.", alias="company_id")
    content_type: Optional[str] = Field(None, description="document content type.", alias="content_type")
    created_at: str = Field(..., description="creation date of the document.", alias="created_at")
    employee_id: Optional[int] = Field(None, description="employee identifier associated to the document.", alias="employee_id")
    extension: Optional[str] = Field(None, description="document extension.", alias="extension")
    file_size: Optional[int] = Field(None, description="document file size in bytes.", alias="file_size")
    filename: str = Field(..., description="name of the document.", alias="filename")
    folder_id: Optional[int] = Field(None, description="folder identifier, references to documents/folders endpoint.", alias="folder_id")
    is_company_document: Optional[bool] = Field(None, description="flag that indicates if the document is a company document.", alias="is_company_document")
    is_management_document: Optional[bool] = Field(None, description="flag that indicates if the document is a management document.", alias="is_management_document")
    is_pending_assignment: Optional[bool] = Field(None, description="flag that indicates if the document is pending assignment.", alias="is_pending_assignment")
    leave_id: Optional[int] = Field(None, description="leave identifier associated to the document, refers to /timeoff/leaves endpoint.", alias="leave_id")
    public: bool = Field(..., description="flag to indicate if the document is public.", alias="public")
    signature_status: Optional[Annotated[str, StringConstraints(pattern=r'^pending|partially_signed|declined|completed|bounced_email|cancelled|error|expired$', strip_whitespace=True)]] = Field(None, description="document signature status.", alias="signature_status")
    signees: Optional[str] = Field(None, description="list of signee access identifiers associated to the document, refers to /employees/employees endpoint.", alias="signees")
    space: str = Field(..., description="document space.", alias="space")
    updated_at: str = Field(..., description="last update date of the document.", alias="updated_at")
    deleted_at: Optional[str] = Field(None, description="deletion date of the document.", alias="deleted_at")

class DocumentsDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

class FoldersCreate(BaseModel):
    company_id: int = Field(..., description="Company ID", alias="company_id")
    name: str = Field(..., description="Folder name", alias="name")
    space: str = Field(..., description="The space of the folder is related to the type of documents that will be stored in it. You should always use "employee_my_documents"", alias="space")

class FoldersUpdate(BaseModel):
    id: int = Field(..., description="ID", alias="id")
    active: bool = Field(..., description="Whether the folder is active or not", alias="active")
    company_id: Optional[int] = Field(None, description="Company ID of the folder", alias="company_id")
    name: str = Field(..., description="Folder name", alias="name")
    parent_folder_id: Optional[int] = Field(None, description="Id of the parent folder", alias="parent_folder_id")
    space: str = Field(..., description="The space of the folder is related to the place where the folder is displayed.", alias="space")

class FoldersDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

