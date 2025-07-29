"""
Financial models for business and medical practice management.
"""

import datetime
import io
from decimal import Decimal
from functools import cached_property
from typing import Optional, Dict, Any, List

from pydantic import BaseModel, computed_field, Field

from .bases import MongoModel, ObjectReferenceId, StrEnum
from .. import fields as fd


def today() -> datetime.date:
    """Get current date."""
    return datetime.date.today()


class ExpenseCategory(MongoModel):
    """
    Represents an expense category for better financial organization and budgeting.
    Supports hierarchical categories with parent-child relationships.
    """
    COLLECTION_NAME = 'expense_category'
    
    name: str
    parent_category_key: Optional[str] = None  # For hierarchical categories
    budget_allocated: Decimal = Field(default=Decimal('0'))
    description: Optional[str] = None
    active: bool = Field(default=True)
    icon: Optional[str] = None  # For UI display (e.g., "APARTMENT" for rent)
    color: Optional[str] = None  # For UI visualization
    created: fd.DefaultDateTime = Field(default_factory=datetime.datetime.now)
    
    def __str__(self):
        """Returns the category name with parent if applicable."""
        if self.parent_category_key:
            parent = ExpenseCategory.find_one({'key': self.parent_category_key})
            if parent:
                return f"{parent.name} > {self.name}"
        return self.name
    
    @cached_property
    def parent_category(self):
        """Get the parent category if exists."""
        if self.parent_category_key:
            return ExpenseCategory.find_one({'key': self.parent_category_key})
        return None
    
    @property
    def subcategories(self):
        """Get all subcategories of this category."""
        return ExpenseCategory.find({'parent_category_key': self.key})


class PaymentTerms(StrEnum):
    """Payment terms enumeration."""
    IMMEDIATE = 'À Vista'
    NET_7 = '7 dias'
    NET_15 = '15 dias'
    NET_30 = '30 dias'
    NET_60 = '60 dias'
    NET_90 = '90 dias'
    CUSTOM = 'Personalizado'


class RecurrencePattern(StrEnum):
    """Recurrence pattern for recurring expenses."""
    DAILY = 'Diário'
    WEEKLY = 'Semanal'
    BIWEEKLY = 'Quinzenal'
    MONTHLY = 'Mensal'
    QUARTERLY = 'Trimestral'
    SEMIANNUAL = 'Semestral'
    ANNUAL = 'Anual'


class Service(MongoModel):
    """
    Represents a service with attributes such as name, price, and discount.
    """
    COLLECTION_NAME = 'service'
    
    active: bool = Field(default=True)
    provider: Optional[ObjectReferenceId] = None
    created: fd.DefaultDateTime = Field(default_factory=datetime.datetime.now)
    name: str
    price: Decimal = Field(default=Decimal('0'))
    return_days: int = Field(default=0)
    max_discount: Decimal = Field(default=Decimal('0'))
    notes: list[str] = Field(default_factory=list)

    def __str__(self):
        """
        Returns a string representation of the service, including its name and price.
        """
        if self.price:
            return f"{self.name} (R$ {self.price})"
        return f'{self.name}'

    @property
    def discount_limit(self):
        """
        Calculates the discount limit based on the price and maximum discount.
        """
        return self.price * self.max_discount


class FinancialAccount(MongoModel):
    """
    Represents a financial account with attributes such as bank details and account type.
    """
    COLLECTION_NAME = 'account'

    class Method(StrEnum):
        CA = 'Dinheiro'
        PI = 'PIX'
        CH = 'Cheque'
        CC = 'Cartão de Crédito'
        CD = 'Cartão de Débito'
        TR = 'Transferência Bancária'
        DC = 'Débito'
        BB = 'Boleto Bancário'

    bank: Optional[str] = None
    agency: Optional[str] = None
    number: Optional[str] = None
    digit: Optional[str] = None
    method: Method
    active: bool = Field(default=True)
    allow_discount: bool = Field(default=False)
    requires_invoice: bool = Field(default=False)

    class AccountType(StrEnum):
        # debit accounts
        D = 'Dividendo'
        E = 'Despesa'
        A = 'Ativo'
        # credit accounts
        L = 'Passivo'
        S = 'Equidade'
        R = 'Receita'

    account_type: AccountType

    def __str__(self):
        """
        Returns a string representation of the financial account, including method and bank details.
        """
        with io.StringIO() as f:
            f.write(f'{self.method.value}')
            if self.bank:
                f.write(f' {self.bank} ')
                if self.agency and self.number and self.digit:
                    f.write(f'{self.agency}:{self.number}-{self.digit} ')
                elif self.agency and self.number:
                    f.write(f'{self.agency}:{self.number} ')
            return f.getvalue()


class FinancialRecord(MongoModel):
    """
    Represents a financial record with transactions and related attributes.
    """
    
    class Transaction(BaseModel):
        """
        Represents a financial transaction with attributes such as amount, account key, and date.
        """
        amount: Decimal
        account_key: str
        date: datetime.date = Field(default_factory=datetime.date.today)
        creator: Optional[ObjectReferenceId] = None

        def __str__(self):
            return f'R$ {self.amount} {self.account_key} {self.date}'

    created: fd.DefaultDateTime = Field(default_factory=datetime.datetime.now)
    creator: Optional[ObjectReferenceId] = None
    date: datetime.date = Field(default_factory=today)
    amount: Optional[Decimal] = Field(default=Decimal('0'))
    description: Optional[str] = None
    transactions: list[Transaction] = Field(default_factory=list)

    def __lt__(self, other):
        """
        Compares two financial records based on their date.
        """
        return self.date < other.date

    def __str__(self):
        """
        Returns a string representation of the financial record, including date and amount.
        """
        return f"{self.date}: R$ {self.amount} ({'finalizada' if self.finished else self.balance})"

    @property
    def sum_transactions(self):
        """
        Sums the amounts of all transactions in the financial record.
        """
        return sum([i.amount for i in self.transactions])

    @computed_field
    @property
    def finished(self) -> bool:
        """
        Checks if the financial record is finished.
        For revenues: automatically finished if amount == 0 (free services/returns), 
                     otherwise finished only when amount > 0 and balance == 0 (fully paid)
        For expenses: finished when amount == sum_transactions
        """
        # If this is a Revenue, handle zero-value revenues as automatically finished
        if hasattr(self, 'patient_key'):  # Revenue has patient_key, Expense doesn't
            # Zero-value revenues (like returns) are automatically finished
            if self.amount == 0:
                return True
            # Revenues with value > 0 are only finished when fully paid
            return self.amount > 0 and self.balance == 0
        # For expenses, use the original logic
        return self.amount == self.sum_transactions

    @property
    def balance(self) -> Decimal:
        """
        Calculates the balance of the financial record by subtracting the total amount from the sum of transactions.
        """
        return self.sum_transactions - self.amount


class RevenueStatus(StrEnum):
    """Revenue status enumeration."""
    SCHEDULED = 'Agendada'
    CONFIRMED = 'Confirmada'
    CANCELLED = 'Cancelada'
    REFUNDED = 'Reembolsada'
    PENDING = 'Pendente'
    PAID = 'Paga'


class PaymentSource(StrEnum):
    """Payment source enumeration for Brazilian healthcare context."""
    SUS = 'SUS'
    PRIVATE_INSURANCE = 'Convênio Particular'
    COMPANY_INSURANCE = 'Convênio Empresarial'
    OUT_OF_POCKET = 'Particular'
    INSURANCE_COPAY = 'Coparticipação'
    VOUCHER = 'Voucher/Benefício'
    OTHER = 'Outros'


class Revenue(FinancialRecord):
    """
    Represents a revenue record, extending FinancialRecord with patient and service keys.
    Enhanced with payment tracking and financial health indicators.
    """
    COLLECTION_NAME = 'revenue'
    
    patient_key: Optional[str] = None
    service_key: Optional[str] = None
    
    # Enhanced fields for financial health analysis
    status: RevenueStatus = Field(default=RevenueStatus.PENDING)
    payment_source: PaymentSource = Field(default=PaymentSource.OUT_OF_POCKET)
    due_date: Optional[datetime.date] = None
    discount_applied: Decimal = Field(default=Decimal('0'))
    payment_terms: PaymentTerms = Field(default=PaymentTerms.IMMEDIATE)
    invoice_number: Optional[str] = None
    tax_amount: Decimal = Field(default=Decimal('0'))
    payment_reminder_sent: bool = Field(default=False)
    collection_attempts: int = Field(default=0)
    last_collection_attempt: Optional[datetime.datetime] = None
    
    # Healthcare-specific fields
    insurance_authorization: Optional[str] = None
    insurance_policy_number: Optional[str] = None
    copay_amount: Decimal = Field(default=Decimal('0'))
    procedure_code: Optional[str] = None  # TISS or ANS procedure codes
    
    # Integration fields
    external_invoice_id: Optional[str] = None
    tax_document_number: Optional[str] = None
    bank_reconciliation_status: Optional[str] = None

    def save_self(self, **kwargs):
        """Save the revenue with automatic status calculation."""
        # Force the finished status to be calculated based on transactions
        data = self.as_json(**kwargs)
        data['finished'] = self.finished
        
        result = self.DATABASE.save_one(self.COLLECTION_NAME, data)
        if result:
            return type(self)(**result)
        return None

    @cached_property
    def patient(self):
        """
        Retrieves the patient associated with the revenue record using the patient key.
        """
        if self.patient_key:
            from .people import Patient
            return Patient.find_one({'key': self.patient_key})
        return None

    @cached_property
    def service(self):
        """
        Retrieves the service associated with the revenue record using the service key.
        """
        if self.service_key:
            return Service.find_one({'key': self.service_key})
        return None
    
    @property
    def net_amount(self) -> Decimal:
        """Calculate net amount after discount and tax."""
        return self.amount - self.discount_applied + self.tax_amount
    
    @property
    def days_overdue(self) -> int:
        """Calculate days overdue if payment is late."""
        if self.due_date and not self.finished:
            current_today = today()
            if current_today > self.due_date:
                return (current_today - self.due_date).days
        return 0
    
    @property
    def is_overdue(self) -> bool:
        """Check if payment is overdue."""
        return self.days_overdue > 0
    
    @property
    def collection_efficiency(self) -> float:
        """Calculate collection efficiency percentage."""
        if self.amount > 0:
            return float(self.sum_transactions / self.amount) * 100
        return 100.0 if self.finished else 0.0


class TherapyPackage(MongoModel):
    """
    Represents a therapy package for continuous session management.
    Used for psychiatric clinics to manage ongoing treatment packages.
    """
    COLLECTION_NAME = 'therapy_package'
    
    patient_key: str
    service_key: str  # Base service for the therapy
    package_name: str
    total_sessions: int
    sessions_used: int = Field(default=0)
    price_per_session: Decimal
    total_amount: Decimal
    discount_percentage: Decimal = Field(default=Decimal('0'))
    
    # Package validity
    start_date: datetime.date
    expiry_date: Optional[datetime.date] = None
    
    # Financial tracking
    amount_paid: Decimal = Field(default=Decimal('0'))
    payment_status: str = Field(default='pending')  # pending, partial, completed
    
    # Metadata
    active: bool = Field(default=True)
    created: fd.DefaultDateTime = Field(default_factory=datetime.datetime.now)
    notes: Optional[str] = None
    
    def __str__(self):
        return f"{self.package_name} - {self.patient.name if self.patient else 'N/A'}"
    
    @cached_property
    def patient(self):
        """Get the patient associated with this package."""
        if self.patient_key:
            from .people import Patient
            return Patient.find_one({'key': self.patient_key})
        return None
    
    @cached_property
    def service(self):
        """Get the service associated with this package."""
        if self.service_key:
            return Service.find_one({'key': self.service_key})
        return None
    
    @property
    def sessions_remaining(self) -> int:
        """Calculate remaining sessions in the package."""
        return max(0, self.total_sessions - self.sessions_used)
    
    @property
    def usage_percentage(self) -> float:
        """Calculate percentage of sessions used."""
        if self.total_sessions > 0:
            return (self.sessions_used / self.total_sessions) * 100
        return 0.0
    
    @property
    def is_expired(self) -> bool:
        """Check if package has expired."""
        if self.expiry_date:
            return today() > self.expiry_date
        return False
    
    @property
    def payment_percentage(self) -> float:
        """Calculate percentage of package paid."""
        if self.total_amount > 0:
            return float(self.amount_paid / self.total_amount) * 100
        return 0.0
    
    @property
    def discounted_amount(self) -> Decimal:
        """Calculate total amount after discount."""
        if self.discount_percentage > 0:
            discount = self.total_amount * (self.discount_percentage / 100)
            return self.total_amount - discount
        return self.total_amount
    
    def use_session(self) -> bool:
        """Use one session from the package. Returns True if successful."""
        if self.sessions_remaining > 0 and not self.is_expired:
            self.sessions_used += 1
            self.save_self()
            return True
        return False
    
    def add_payment(self, amount: Decimal) -> None:
        """Add payment to the package and update status."""
        self.amount_paid += amount
        
        # Update payment status
        payment_percentage = self.payment_percentage
        if payment_percentage >= 100:
            self.payment_status = 'completed'
        elif payment_percentage > 0:
            self.payment_status = 'partial'
        else:
            self.payment_status = 'pending'
        
        self.save_self()


class Expense(FinancialRecord):
    """
    Represents an expense record, extending FinancialRecord with categorization and tracking.
    Enhanced with budgeting and approval workflow fields.
    """
    COLLECTION_NAME = 'expense'
    
    description: str
    
    # Enhanced categorization and tracking
    category_key: Optional[str] = None
    subcategory: Optional[str] = None
    vendor_key: Optional[str] = None  # Reference to a Vendor model (future)
    vendor_name: Optional[str] = None  # Fallback for vendor info
    
    # Recurrence management
    recurring: bool = Field(default=False)
    recurrence_pattern: Optional[RecurrencePattern] = None
    next_recurrence_date: Optional[datetime.date] = None
    parent_expense_key: Optional[str] = None  # For tracking recurring expense origin
    
    # Approval workflow
    approved_by: Optional[ObjectReferenceId] = None
    approval_date: Optional[datetime.datetime] = None
    approval_required: bool = Field(default=False)
    approval_notes: Optional[str] = None
    
    # Budget tracking
    budget_category: Optional[str] = None
    cost_center: Optional[str] = None
    
    # Additional tracking fields
    invoice_number: Optional[str] = None
    payment_due_date: Optional[datetime.date] = None
    priority: str = Field(default="normal")  # low, normal, high, critical
    
    @cached_property
    def category(self):
        """Get the expense category object."""
        if self.category_key:
            return ExpenseCategory.find_one({'key': self.category_key})
        return None
    
    @property
    def is_approved(self) -> bool:
        """Check if expense is approved."""
        return bool(self.approved_by and self.approval_date)
    
    @property
    def days_until_due(self) -> int:
        """Calculate days until payment is due."""
        if self.payment_due_date:
            current_today = today()
            if self.payment_due_date > current_today:
                return (self.payment_due_date - current_today).days
            return 0
        return 0
    
    @property
    def is_overdue(self) -> bool:
        """Check if payment is overdue."""
        if self.payment_due_date and not self.finished:
            return today() > self.payment_due_date
        return False
    
    def create_recurrence(self) -> Optional['Expense']:
        """Create the next recurring expense based on pattern."""
        if not self.recurring or not self.recurrence_pattern or not self.next_recurrence_date:
            return None
        
        # Calculate next date based on pattern
        next_date = self.next_recurrence_date
        if self.recurrence_pattern == RecurrencePattern.DAILY:
            new_next_date = next_date + datetime.timedelta(days=1)
        elif self.recurrence_pattern == RecurrencePattern.WEEKLY:
            new_next_date = next_date + datetime.timedelta(weeks=1)
        elif self.recurrence_pattern == RecurrencePattern.BIWEEKLY:
            new_next_date = next_date + datetime.timedelta(weeks=2)
        elif self.recurrence_pattern == RecurrencePattern.MONTHLY:
            # Handle month-end dates properly
            if next_date.month == 12:
                new_next_date = next_date.replace(year=next_date.year + 1, month=1)
            else:
                new_next_date = next_date.replace(month=next_date.month + 1)
        elif self.recurrence_pattern == RecurrencePattern.QUARTERLY:
            new_next_date = next_date + datetime.timedelta(days=90)
        elif self.recurrence_pattern == RecurrencePattern.SEMIANNUAL:
            new_next_date = next_date + datetime.timedelta(days=180)
        elif self.recurrence_pattern == RecurrencePattern.ANNUAL:
            new_next_date = next_date.replace(year=next_date.year + 1)
        else:
            return None
        
        # Create new expense
        new_expense = Expense(
            description=self.description,
            amount=self.amount,
            date=self.next_recurrence_date,
            category_key=self.category_key,
            subcategory=self.subcategory,
            vendor_key=self.vendor_key,
            vendor_name=self.vendor_name,
            recurring=True,
            recurrence_pattern=self.recurrence_pattern,
            next_recurrence_date=new_next_date,
            parent_expense_key=self.key,
            budget_category=self.budget_category,
            cost_center=self.cost_center,
            payment_due_date=self.next_recurrence_date + datetime.timedelta(days=30) if self.payment_due_date else None,
            creator=self.creator
        )
        
        return new_expense


class Budget(MongoModel):
    """
    Represents a budget for a specific period with category allocations.
    Used for financial planning and expense control.
    """
    COLLECTION_NAME = 'budget'
    
    name: str
    period_start: datetime.date
    period_end: datetime.date
    category_budgets: Dict[str, Decimal] = Field(default_factory=dict)  # category_key -> amount
    total_budget: Decimal = Field(default=Decimal('0'))
    created_by: ObjectReferenceId
    created: fd.DefaultDateTime = Field(default_factory=datetime.datetime.now)
    approved: bool = Field(default=False)
    approved_by: Optional[ObjectReferenceId] = None
    approved_date: Optional[datetime.datetime] = None
    active: bool = Field(default=True)
    notes: Optional[str] = None
    
    def __str__(self):
        """Return budget name with period."""
        return f"{self.name} ({self.period_start.strftime('%m/%Y')} - {self.period_end.strftime('%m/%Y')})"
    
    @property
    def days_remaining(self) -> int:
        """Calculate days remaining in budget period."""
        current_today = today()
        if current_today > self.period_end:
            return 0
        return (self.period_end - current_today).days
    
    @property
    def is_active(self) -> bool:
        """Check if budget is currently active."""
        current_today = today()
        return self.active and self.period_start <= current_today <= self.period_end
    
    def get_category_usage(self, category_key: str) -> Dict[str, Any]:
        """Get usage statistics for a specific category."""
        if category_key not in self.category_budgets:
            return {'allocated': 0, 'used': 0, 'remaining': 0, 'percentage': 0}
        
        allocated = self.category_budgets[category_key]
        
        # Calculate actual expenses for this category in the budget period
        expenses = Expense.find({
            'category_key': category_key,
            'date': {
                '$gte': self.period_start.isoformat(),
                '$lte': self.period_end.isoformat()
            }
        })
        
        used = sum(exp.amount for exp in expenses)
        remaining = allocated - used
        percentage = float(used / allocated) * 100 if allocated > 0 else 0
        
        return {
            'allocated': allocated,
            'used': used,
            'remaining': remaining,
            'percentage': percentage,
            'is_over_budget': used > allocated
        }