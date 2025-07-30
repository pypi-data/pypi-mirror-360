# Auto-generated schemas for category: finance

import pandas as pd
import pandera as pa
from pandera.typing import Series, String, Int, Float, Bool, DateTime
import pandera.extensions as extensions
from brynq_sdk_functions import BrynQPanderaDataFrameModel
from typing import Optional, Annotated
from pydantic import BaseModel, Field, StringConstraints

class Accounting_settingsGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Identifier for the AccountingSetting.", alias="id")
    external_id: Series[String] = pa.Field(coerce=True, nullable=True, description="External ID for the accounting setting.", alias="external_id")
    company_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="ID of the associated Company.", alias="company_id")
    legal_entity_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="ID of the associated Legal Entity.", alias="legal_entity_id")
    updated_at: Series[String] = pa.Field(coerce=True, nullable=False, description="Timestamp when the accounting setting was last updated.", alias="updated_at")
    default_account_for_purchase_invoices_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="Default account for purchase invoices.", alias="default_account_for_purchase_invoices_id")
    default_account_for_vendors_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="Default account for vendors.", alias="default_account_for_vendors_id")
    default_account_for_banks_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="Default account for banks.", alias="default_account_for_banks_id")
    default_account_for_suspense_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="Default suspense account.", alias="default_account_for_suspense_id")
    default_account_for_expenses_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="Default account for expenses.", alias="default_account_for_expenses_id")
    default_account_for_employees_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="Default account for employees.", alias="default_account_for_employees_id")
    default_account_for_sale_invoices_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="Default account for sale invoices.", alias="default_account_for_sale_invoices_id")
    default_account_for_clients_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="Default account for clients.", alias="default_account_for_clients_id")
    default_account_for_benefits_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="Default account for benefits.", alias="default_account_for_benefits_id")

    class _Annotation:
        primary_key = "id"
        foreign_keys = {
            "legal_entity_id": {
                "parent_schema": "Legal_entitiesGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "default_account_for_purchase_invoices_id": {
                "parent_schema": "AccountsGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "default_account_for_vendors_id": {
                "parent_schema": "AccountsGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "default_account_for_banks_id": {
                "parent_schema": "AccountsGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "default_account_for_suspense_id": {
                "parent_schema": "AccountsGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "default_account_for_expenses_id": {
                "parent_schema": "AccountsGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "default_account_for_employees_id": {
                "parent_schema": "AccountsGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "default_account_for_sale_invoices_id": {
                "parent_schema": "AccountsGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "default_account_for_clients_id": {
                "parent_schema": "AccountsGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "default_account_for_benefits_id": {
                "parent_schema": "AccountsGet",
                "parent_column": "id",
                "cardinality": "N:1"
            }
        }

class AccountsGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Unique identifier in factorial for the ledger account", alias="id")
    name: Series[String] = pa.Field(coerce=True, nullable=True, description="Name of the ledger account", alias="name")
    legal_entity_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Legal entity ID of the ledger account", alias="legal_entity_id")
    number: Series[String] = pa.Field(coerce=True, nullable=False, description="Number of the ledger account", alias="number")
    disabled: Series[Bool] = pa.Field(coerce=True, nullable=False, description="Whether the ledger account is disabled", alias="disabled")
    type: Series[String] = pa.Field(coerce=True, nullable=False, description="Type of the ledger account", alias="type")
    external_id: Series[String] = pa.Field(coerce=True, nullable=True, description="Id of the ledger account on the external system", alias="external_id")
    updated_at: Series[String] = pa.Field(coerce=True, nullable=False, description="Last updated date of the ledger account", alias="updated_at")

    class _Annotation:
        primary_key = "id"
        foreign_keys = {
            "legal_entity_id": {
                "parent_schema": "Legal_entitiesGet",
                "parent_column": "id",
                "cardinality": "N:1"
            }
        }

class ContactsGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Unique identifier for the Contact.", alias="id")
    tax_id: Series[String] = pa.Field(coerce=True, nullable=False, description="Tax identification number assigned to the Contact.", alias="tax_id")
    legal_name: Series[String] = pa.Field(coerce=True, nullable=False, description="The official or legal name of the Contact.", alias="legal_name")
    address: Series[String] = pa.Field(coerce=True, nullable=False, description="The address object containing street, city, etc.", alias="address")
    external_id: Series[String] = pa.Field(coerce=True, nullable=True, description="The external id of the contact.", alias="external_id")
    updated_at: Series[String] = pa.Field(coerce=True, nullable=False, description="Timestamp when the Contact was last updated.", alias="updated_at")
    iban: Series[String] = pa.Field(coerce=True, nullable=True, description="International Bank Account Number if provided.", alias="iban")
    bank_code: Series[String] = pa.Field(coerce=True, nullable=True, description="Bank or branch code for the Contact if relevant.", alias="bank_code")
    preferred_payment_method: Series[String] = pa.Field(coerce=True, nullable=True, description="Preferred payment method for the Contact (e.g. wire_transfer, paypal).", alias="preferred_payment_method")

    class _Annotation:
        primary_key = "id"
        foreign_keys = {}

class Cost_centersGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="", alias="id")
    name: Series[String] = pa.Field(coerce=True, nullable=False, description="", alias="name")
    company_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="", alias="company_id")
    legal_entity_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="", alias="legal_entity_id")
    code: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="code")
    description: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="description")
    active_employees_count: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="", alias="active_employees_count")
    historical_employees_count: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="", alias="historical_employees_count")
    status: Series[String] = pa.Field(coerce=True, nullable=False, description="", alias="status")
    deactivation_date: Series[String] = pa.Field(coerce=True, nullable=True, description="", alias="deactivation_date")

    class _Annotation:
        primary_key = "id"
        foreign_keys = {
            "legal_entity_id": {
                "parent_schema": "Legal_entitiesGet",
                "parent_column": "id",
                "cardinality": "N:1"
            }
        }

class Financial_documentsGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Factorial unique identifier.", alias="id")
    net_amount_cents: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="Net amount in cents.", alias="net_amount_cents")
    total_amount_cents: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="Total amount in cents.", alias="total_amount_cents")
    document_number: Series[String] = pa.Field(coerce=True, nullable=True, description="Document number.", alias="document_number")
    currency: Series[String] = pa.Field(coerce=True, nullable=True, description="Document currency.", alias="currency")
    status: Series[String] = pa.Field(coerce=True, nullable=False, description="Current status.", alias="status")
    due_date: Series[String] = pa.Field(coerce=True, nullable=True, description="Due date.", alias="due_date")
    document_date: Series[String] = pa.Field(coerce=True, nullable=True, description="Document date.", alias="document_date")
    legal_entity_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="Factorial unique identifier for the legal entity of the financial document.", alias="legal_entity_id")
    vendor_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="Factorial unique identifier for the vendor of the financial document.", alias="vendor_id")
    file: Series[String] = pa.Field(coerce=True, nullable=True, description="File attached.", alias="file")
    updated_at: Series[String] = pa.Field(coerce=True, nullable=False, description="Updation date.", alias="updated_at")
    taxes: Series[String] = pa.Field(coerce=True, nullable=False, description="Taxes.", alias="taxes")
    fully_reconciled_at: Series[String] = pa.Field(coerce=True, nullable=True, description="Date when was fully reconciled.", alias="fully_reconciled_at")
    recorded_at: Series[String] = pa.Field(coerce=True, nullable=True, description="Date when was recorded.", alias="recorded_at")
    duplicate_financial_document_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="Factorial unique identifier for the duplicate financial document.", alias="duplicate_financial_document_id")
    validated_at: Series[String] = pa.Field(coerce=True, nullable=True, description="Date when was validated.", alias="validated_at")
    validated_by_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="Factorial unique identifier for the user who validated the financial document.", alias="validated_by_id")
    document_type: Series[String] = pa.Field(coerce=True, nullable=False, description="Type of the financial document. Using 'invoice' as default.", alias="document_type")
    parent_financial_document_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="Factorial unique identifier for the parent financial document of the financial document.", alias="parent_financial_document_id")
    taxes_total_amount_cents: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="Taxes total amount in cents.", alias="taxes_total_amount_cents")

    class _Annotation:
        primary_key = "id"
        foreign_keys = {
            "legal_entity_id": {
                "parent_schema": "Legal_entitiesGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "vendor_id": {
                "parent_schema": "ContactsGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "duplicate_financial_document_id": {
                "parent_schema": "Financial_documentsGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "validated_by_id": {
                "parent_schema": "UserSchema",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "parent_financial_document_id": {
                "parent_schema": "Financial_documentsGet",
                "parent_column": "id",
                "cardinality": "N:1"
            }
        }

class Journal_entriesGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Journal entry ID", alias="id")
    number: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Incremental number assigned to the journal entry", alias="number")
    published_at: Series[String] = pa.Field(coerce=True, nullable=False, description="Timestamp when the journal entry was published.", alias="published_at")
    type: Series[String] = pa.Field(coerce=True, nullable=False, description="Journal entry type (e.g. bank, invoice, tax)", alias="type")
    source_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="Source id related with this journal entry", alias="source_id")
    source_type: Series[String] = pa.Field(coerce=True, nullable=True, description="Source type related with this journal entry", alias="source_type")
    reference_date: Series[String] = pa.Field(coerce=True, nullable=False, description="Date of the associate source", alias="reference_date")
    description: Series[String] = pa.Field(coerce=True, nullable=True, description="Description of the journal entry", alias="description")
    legal_entity_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="The associated Legal Entity ID", alias="legal_entity_id")
    external_id: Series[String] = pa.Field(coerce=True, nullable=True, description="External identifier for the journal entry", alias="external_id")
    status: Series[String] = pa.Field(coerce=True, nullable=False, description="The status of the journal entry (draft, published, etc.)", alias="status")
    updated_at: Series[String] = pa.Field(coerce=True, nullable=False, description="Timestamp when the journal entry was last updated.", alias="updated_at")

    class _Annotation:
        primary_key = "id"
        foreign_keys = {
            "legal_entity_id": {
                "parent_schema": "Legal_entitiesGet",
                "parent_column": "id",
                "cardinality": "N:1"
            }
        }

class Journal_linesGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Factorial id", alias="id")
    number: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Sequential number assigned to the line", alias="number")
    debit_amount_cents: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="The debit amount in cents", alias="debit_amount_cents")
    credit_amount_cents: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="The credit amount in cents", alias="credit_amount_cents")
    journal_entry_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="ID of the parent journal entry", alias="journal_entry_id")
    account_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="ID of the associated account", alias="account_id")
    fully_reconciled_at: Series[String] = pa.Field(coerce=True, nullable=True, description="Timestamp when the journal line was reconciled", alias="fully_reconciled_at")
    external_id: Series[String] = pa.Field(coerce=True, nullable=True, description="External identifier for the journal line", alias="external_id")
    updated_at: Series[String] = pa.Field(coerce=True, nullable=False, description="Timestamp when the journal line was last updated.", alias="updated_at")

    class _Annotation:
        primary_key = "id"
        foreign_keys = {
            "journal_entry_id": {
                "parent_schema": "Journal_entriesGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "account_id": {
                "parent_schema": "AccountsGet",
                "parent_column": "id",
                "cardinality": "N:1"
            }
        }

class Ledger_account_resourcesGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Factorial unique identifier.", alias="id")
    resource_type: Series[String] = pa.Field(coerce=True, nullable=False, description="Ledger account resource type.", alias="resource_type")
    resource_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Factorial unique identifier of the resource associated to the ledger account resource.", alias="resource_id")
    account_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Factorial Ledger Account identifier.", alias="account_id")
    balance_type: Series[String] = pa.Field(coerce=True, nullable=True, description="Ledger account balance type.", alias="balance_type")
    updated_at: Series[String] = pa.Field(coerce=True, nullable=False, description="Last time the resource was updated.", alias="updated_at")
    external_id: Series[String] = pa.Field(coerce=True, nullable=True, description="External identifier.", alias="external_id")
    legal_entity_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=True, description="Factorial unique identifier of the Legal entity.", alias="legal_entity_id")

    class _Annotation:
        primary_key = "id"
        foreign_keys = {
            "account_id": {
                "parent_schema": "AccountsGet",
                "parent_column": "id",
                "cardinality": "N:1"
            },
            "legal_entity_id": {
                "parent_schema": "Legal_entitiesGet",
                "parent_column": "id",
                "cardinality": "N:1"
            }
        }

class Tax_ratesGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Factorial id", alias="id")
    rate: Series[Float] = pa.Field(coerce=True, nullable=False, description="Specifies the numerical percentage for the tax rate between -1 and 1.", alias="rate")
    description: Series[String] = pa.Field(coerce=True, nullable=True, description="An optional text describing the tax rate's purpose or context.", alias="description")
    tax_type_id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="The identifier of the related TaxType record.", alias="tax_type_id")
    external_id: Series[String] = pa.Field(coerce=True, nullable=True, description="The external id of the tax rate.", alias="external_id")
    updated_at: Series[String] = pa.Field(coerce=True, nullable=False, description="Last update date of the tax rate.", alias="updated_at")

    class _Annotation:
        primary_key = "id"
        foreign_keys = {
            "tax_type_id": {
                "parent_schema": "Tax_typesGet",
                "parent_column": "id",
                "cardinality": "N:1"
            }
        }

class Tax_typesGet(BrynQPanderaDataFrameModel):
    id: Series[pd.Int64Dtype] = pa.Field(coerce=True, nullable=False, description="Factorial id", alias="id")
    name: Series[String] = pa.Field(coerce=True, nullable=False, description="The name assigned to the tax type.", alias="name")
    type: Series[String] = pa.Field(coerce=True, nullable=False, description="The tax category used to distinguish different tax kinds.", alias="type")
    country_code: Series[String] = pa.Field(coerce=True, nullable=True, description="The country code where this tax type applies.", alias="country_code")
    external_id: Series[String] = pa.Field(coerce=True, nullable=True, description="The external id of the tax type.", alias="external_id")
    updated_at: Series[String] = pa.Field(coerce=True, nullable=False, description="Last update date of the tax type.", alias="updated_at")

    class _Annotation:
        primary_key = "id"
        foreign_keys = {}

class Accounting_settingsCreate(BaseModel):
    id: int = Field(..., description="Identifier for the AccountingSetting.", alias="id")
    external_id: Optional[str] = Field(None, description="External ID for the accounting setting.", alias="external_id")
    company_id: int = Field(..., description="ID of the associated Company.", alias="company_id")
    legal_entity_id: int = Field(..., description="ID of the associated Legal Entity.", alias="legal_entity_id")
    updated_at: str = Field(..., description="Timestamp when the accounting setting was last updated.", alias="updated_at")
    default_account_for_purchase_invoices_id: Optional[int] = Field(None, description="Default account for purchase invoices.", alias="default_account_for_purchase_invoices_id")
    default_account_for_vendors_id: Optional[int] = Field(None, description="Default account for vendors.", alias="default_account_for_vendors_id")
    default_account_for_banks_id: Optional[int] = Field(None, description="Default account for banks.", alias="default_account_for_banks_id")
    default_account_for_suspense_id: Optional[int] = Field(None, description="Default suspense account.", alias="default_account_for_suspense_id")
    default_account_for_expenses_id: Optional[int] = Field(None, description="Default account for expenses.", alias="default_account_for_expenses_id")
    default_account_for_employees_id: Optional[int] = Field(None, description="Default account for employees.", alias="default_account_for_employees_id")
    default_account_for_sale_invoices_id: Optional[int] = Field(None, description="Default account for sale invoices.", alias="default_account_for_sale_invoices_id")
    default_account_for_clients_id: Optional[int] = Field(None, description="Default account for clients.", alias="default_account_for_clients_id")
    default_account_for_benefits_id: Optional[int] = Field(None, description="Default account for benefits.", alias="default_account_for_benefits_id")

class Accounting_settingsDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

class AccountsCreate(BaseModel):
    name: Optional[str] = Field(None, description="Name of the ledger account", alias="name")
    number: str = Field(..., description="Number of the ledger account", alias="number")
    type: Annotated[str, StringConstraints(pattern=r'^equity|non_current_asset|current_asset|bank|non_current_liability|current_liability|expense|income$', strip_whitespace=True)] = Field(..., description="Type of the ledger account", alias="type")
    currency: str = Field(..., description="Currency of the ledger account", alias="currency")
    legal_entity_id: int = Field(..., description="Legal entity ID of the ledger account", alias="legal_entity_id")
    external_id: Optional[str] = Field(None, description="Id of the ledger account on the external system. This field is important to avoid having duplicated ledger accounts", alias="external_id")

class AccountsUpdate(BaseModel):
    id: int = Field(..., description="ID", alias="id")
    name: Optional[str] = Field(None, description="Name of the ledger account", alias="name")
    legal_entity_id: int = Field(..., description="Legal entity ID of the ledger account", alias="legal_entity_id")
    number: str = Field(..., description="Number of the ledger account", alias="number")
    disabled: bool = Field(..., description="Whether the ledger account is disabled", alias="disabled")
    type: Annotated[str, StringConstraints(pattern=r'^equity|non_current_asset|current_asset|bank|non_current_liability|current_liability|expense|income$', strip_whitespace=True)] = Field(..., description="Type of the ledger account", alias="type")
    external_id: Optional[str] = Field(None, description="Id of the ledger account on the external system", alias="external_id")
    updated_at: str = Field(..., description="Last updated date of the ledger account", alias="updated_at")

class AccountsDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

class ContactsCreate(BaseModel):
    tax_id: str = Field(..., description="Tax identification number assigned to the Contact.", alias="tax_id")
    legal_name: str = Field(..., description="The official or legal name of the Contact.", alias="legal_name")
    address: str = Field(..., description="The address object containing street, city, etc.", alias="address")
    iban: Optional[str] = Field(None, description="International Bank Account Number if provided.", alias="iban")
    bank_code: Optional[str] = Field(None, description="Bank or branch code for the Contact if relevant.", alias="bank_code")
    external_id: Optional[str] = Field(None, description="The external id of the contact.", alias="external_id")
    project_ids: Optional[str] = Field(None, description="List of project IDs associated with the Contact.", alias="project_ids")

class ContactsUpdate(BaseModel):
    id: int = Field(..., description="ID", alias="id")
    tax_id: str = Field(..., description="Tax identification number assigned to the Contact.", alias="tax_id")
    legal_name: str = Field(..., description="The official or legal name of the Contact.", alias="legal_name")
    address: str = Field(..., description="The address object containing street, city, etc.", alias="address")
    external_id: Optional[str] = Field(None, description="The external id of the contact.", alias="external_id")
    updated_at: str = Field(..., description="Timestamp when the Contact was last updated.", alias="updated_at")
    iban: Optional[str] = Field(None, description="International Bank Account Number if provided.", alias="iban")
    bank_code: Optional[str] = Field(None, description="Bank or branch code for the Contact if relevant.", alias="bank_code")
    preferred_payment_method: Optional[Annotated[str, StringConstraints(pattern=r'^card|banktransfer$', strip_whitespace=True)]] = Field(None, description="Preferred payment method for the Contact (e.g. wire_transfer, paypal).", alias="preferred_payment_method")

class ContactsDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

class Cost_centersCreate(BaseModel):
    name: str = Field(..., description="", alias="name")
    company_id: int = Field(..., description="", alias="company_id")
    legal_entity_id: Optional[int] = Field(None, description="", alias="legal_entity_id")
    code: Optional[str] = Field(None, description="", alias="code")
    description: Optional[str] = Field(None, description="", alias="description")

class Cost_centersDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

class Financial_documentsDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

class Journal_entriesCreate(BaseModel):
    external_id: Optional[str] = Field(None, description="External identifier for the journal entry", alias="external_id")
    legal_entity_id: int = Field(..., description="The associated Legal Entity ID", alias="legal_entity_id")
    type: Optional[Annotated[str, StringConstraints(pattern=r'^bank|bill|invoice|credit_note|merged_ledger_account|reconciliation|tax|receipt|payroll_result|external$', strip_whitespace=True)]] = Field(None, description="Journal entry type (e.g. bank, invoice, tax)", alias="type")
    lines: str = Field(..., description="Array of journal lines for this entry, example: [{'account_id': 9876, 'debit_amount_cents': 0, 'credit_amount_cents': 100, 'external_id': 'LINE-001'}, {'account_id': 9876, 'debit_amount_cents': 100, 'credit_amount_cents': 0, 'external_id': 'LINE-002'}]", alias="lines")
    reference_date: str = Field(..., description="Date of the associate source", alias="reference_date")
    description: Optional[str] = Field(None, description="Description of the journal entry", alias="description")
    status: Optional[Annotated[str, StringConstraints(pattern=r'^published|reversed$', strip_whitespace=True)]] = Field(None, description="Status of the journal entry (reversed, published, etc.)", alias="status")

class Journal_entriesDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

class Journal_linesDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

class Ledger_account_resourcesCreate(BaseModel):
    id: int = Field(..., description="Factorial unique identifier.", alias="id")
    resource_type: Annotated[str, StringConstraints(pattern=r'^expensablecategory|customcategory|bankaccount|vendor|taxtype|invoice|payrollconcept$', strip_whitespace=True)] = Field(..., description="Ledger account resource type.", alias="resource_type")
    resource_id: int = Field(..., description="Factorial unique identifier of the resource associated to the ledger account resource.", alias="resource_id")
    account_id: int = Field(..., description="Factorial Ledger Account identifier.", alias="account_id")
    balance_type: Optional[Annotated[str, StringConstraints(pattern=r'^credit|debit$', strip_whitespace=True)]] = Field(None, description="Ledger account balance type.", alias="balance_type")
    updated_at: str = Field(..., description="Last time the resource was updated.", alias="updated_at")
    external_id: Optional[str] = Field(None, description="External identifier.", alias="external_id")
    legal_entity_id: Optional[int] = Field(None, description="Factorial unique identifier of the Legal entity.", alias="legal_entity_id")

class Ledger_account_resourcesDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

class Tax_ratesCreate(BaseModel):
    description: Optional[str] = Field(None, description="An optional text describing the tax rate's purpose or context.", alias="description")
    rate: Optional[float] = Field(None, description="Specifies the numerical percentage for the tax rate between -1 and 1.", alias="rate")
    tax_type_id: Optional[int] = Field(None, description="The identifier of the related TaxType record.", alias="tax_type_id")
    external_id: Optional[str] = Field(None, description="The external id of the tax rate.", alias="external_id")

class Tax_ratesUpdate(BaseModel):
    id: int = Field(..., description="ID", alias="id")
    rate: float = Field(..., description="Specifies the numerical percentage for the tax rate between -1 and 1.", alias="rate")
    description: Optional[str] = Field(None, description="An optional text describing the tax rate's purpose or context.", alias="description")
    tax_type_id: int = Field(..., description="The identifier of the related TaxType record.", alias="tax_type_id")
    external_id: Optional[str] = Field(None, description="The external id of the tax rate.", alias="external_id")
    updated_at: str = Field(..., description="Last update date of the tax rate.", alias="updated_at")

class Tax_ratesDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")

class Tax_typesCreate(BaseModel):
    name: str = Field(..., description="The name assigned to the tax type.", alias="name")
    type: Annotated[str, StringConstraints(pattern=r'^vat|personal_income$', strip_whitespace=True)] = Field(..., description="The tax category used to distinguish different tax kinds.", alias="type")
    country_code: Optional[str] = Field(None, description="The country code where this tax type applies.", alias="country_code")
    external_id: Optional[str] = Field(None, description="The external id of the tax type.", alias="external_id")

class Tax_typesUpdate(BaseModel):
    id: int = Field(..., description="ID", alias="id")
    name: str = Field(..., description="The name assigned to the tax type.", alias="name")
    type: Annotated[str, StringConstraints(pattern=r'^vat|personal_income$', strip_whitespace=True)] = Field(..., description="The tax category used to distinguish different tax kinds.", alias="type")
    country_code: Optional[str] = Field(None, description="The country code where this tax type applies.", alias="country_code")
    external_id: Optional[str] = Field(None, description="The external id of the tax type.", alias="external_id")
    updated_at: str = Field(..., description="Last update date of the tax type.", alias="updated_at")

class Tax_typesDelete(BaseModel):
    id: int = Field(..., description="ID", alias="id")
