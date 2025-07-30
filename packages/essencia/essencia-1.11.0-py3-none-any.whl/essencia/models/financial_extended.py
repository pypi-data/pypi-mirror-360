"""Extended financial models for advanced financial management.

This module provides additional financial models beyond the basic
Revenue and Expense models, including financial goals, cash flow
projections, expense categorization, and therapy package management.
"""

import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from enum import Enum

from pydantic import Field, field_validator, model_validator

from .bases import MongoModel, ObjectReferenceId, StrEnum
from essencia import fields as fd


class GoalType(StrEnum):
    """Types of financial goals."""
    REVENUE = 'REVENUE'
    EXPENSE_REDUCTION = 'EXPENSE_REDUCTION'
    PROFIT_MARGIN = 'PROFIT_MARGIN'
    PATIENT_ACQUISITION = 'PATIENT_ACQUISITION'
    SERVICE_EXPANSION = 'SERVICE_EXPANSION'


class GoalStatus(StrEnum):
    """Status of financial goals."""
    DRAFT = 'DRAFT'
    ACTIVE = 'ACTIVE'
    ACHIEVED = 'ACHIEVED'
    FAILED = 'FAILED'
    CANCELLED = 'CANCELLED'


class PaymentStatus(StrEnum):
    """Payment status for therapy packages."""
    PENDING = 'PENDING'
    PARTIAL = 'PARTIAL'
    PAID = 'PAID'
    OVERDUE = 'OVERDUE'
    CANCELLED = 'CANCELLED'


class ExpenseCategory(MongoModel):
    """Hierarchical expense categorization system."""
    COLLECTION_NAME = 'expense_category'
    
    name: str = Field(..., description="Category name")
    parent_category_key: Optional[ObjectReferenceId] = Field(None, description="Parent category for hierarchy")
    budget_allocated: Optional[Decimal] = Field(None, description="Budget allocated to this category")
    icon: Optional[str] = Field(None, description="Icon for UI display")
    color: Optional[str] = Field(None, description="Color for UI display")
    is_active: bool = Field(True, description="Whether category is active")
    
    creator: ObjectReferenceId = 'doctor.admin'
    created: fd.DefaultDateTime
    
    def get_subcategories(self) -> List['ExpenseCategory']:
        """Get all subcategories of this category."""
        return list(self.__class__.find({'parent_category_key': self.key}))
    
    def get_full_path(self) -> str:
        """Get full category path (e.g., 'Healthcare > Medications')."""
        if not self.parent_category_key:
            return self.name
        
        parent = self.__class__.find_one({'key': self.parent_category_key})
        if parent:
            return f"{parent.get_full_path()} > {self.name}"
        return self.name


class FinancialGoal(MongoModel):
    """Financial targets and performance tracking."""
    COLLECTION_NAME = 'financial_goals'
    
    goal_type: GoalType
    title: str = Field(..., description="Goal title")
    description: Optional[str] = Field(None, description="Detailed description")
    
    # Target metrics
    target_amount: Optional[Decimal] = Field(None, description="Target amount in currency")
    target_percentage: Optional[float] = Field(None, description="Target percentage (e.g., 20% profit margin)")
    target_count: Optional[int] = Field(None, description="Target count (e.g., number of patients)")
    
    # Timeline
    start_date: fd.DefaultDate
    end_date: datetime.date
    
    # Status tracking
    status: GoalStatus = GoalStatus.DRAFT
    current_amount: Optional[Decimal] = Field(None, description="Current progress amount")
    current_percentage: Optional[float] = Field(None, description="Current progress percentage")
    current_count: Optional[int] = Field(None, description="Current progress count")
    
    # Progress milestones
    milestone_updates: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Metadata
    creator: ObjectReferenceId = 'doctor.admin'
    created: fd.DefaultDateTime
    last_updated: Optional[datetime.datetime] = None
    
    def add_milestone(self, amount: Optional[Decimal] = None, 
                     percentage: Optional[float] = None,
                     count: Optional[int] = None,
                     notes: Optional[str] = None) -> None:
        """Add a progress milestone."""
        milestone = {
            'date': datetime.datetime.now(),
            'amount': amount,
            'percentage': percentage,
            'count': count,
            'notes': notes
        }
        self.milestone_updates.append(milestone)
        
        # Update current values
        if amount is not None:
            self.current_amount = amount
        if percentage is not None:
            self.current_percentage = percentage
        if count is not None:
            self.current_count = count
        
        self.last_updated = datetime.datetime.now()
    
    def calculate_progress(self) -> float:
        """Calculate progress percentage towards goal."""
        if self.target_amount and self.current_amount:
            return float(self.current_amount / self.target_amount * 100)
        elif self.target_percentage and self.current_percentage:
            return float(self.current_percentage / self.target_percentage * 100)
        elif self.target_count and self.current_count:
            return float(self.current_count / self.target_count * 100)
        return 0.0
    
    def is_on_track(self) -> bool:
        """Check if goal is on track based on timeline."""
        if self.status != GoalStatus.ACTIVE:
            return False
        
        days_total = (self.end_date - self.start_date).days
        days_elapsed = (datetime.date.today() - self.start_date).days
        
        if days_total <= 0:
            return False
        
        expected_progress = (days_elapsed / days_total) * 100
        actual_progress = self.calculate_progress()
        
        # Consider on track if within 10% of expected progress
        return actual_progress >= (expected_progress - 10)


class CashFlowProjection(MongoModel):
    """Cash flow forecasting and analysis."""
    COLLECTION_NAME = 'cash_flow_projections'
    
    projection_date: datetime.date = Field(..., description="Date for this projection")
    period_type: str = Field(..., description="Period type: daily, weekly, monthly")
    
    # Projections
    expected_revenues: Decimal = Field(default=Decimal('0'), description="Expected revenue")
    expected_expenses: Decimal = Field(default=Decimal('0'), description="Expected expenses")
    expected_net: Decimal = Field(default=Decimal('0'), description="Expected net cash flow")
    
    # Actuals (filled in after the period)
    actual_revenues: Optional[Decimal] = Field(None, description="Actual revenue")
    actual_expenses: Optional[Decimal] = Field(None, description="Actual expenses")
    actual_net: Optional[Decimal] = Field(None, description="Actual net cash flow")
    
    # Variance analysis
    variance_revenues: Optional[Decimal] = Field(None, description="Revenue variance")
    variance_expenses: Optional[Decimal] = Field(None, description="Expense variance")
    variance_net: Optional[Decimal] = Field(None, description="Net variance")
    variance_percentage: Optional[float] = Field(None, description="Overall variance percentage")
    
    # Breakdown by category
    revenue_breakdown: Dict[str, Decimal] = Field(default_factory=dict)
    expense_breakdown: Dict[str, Decimal] = Field(default_factory=dict)
    
    # Metadata
    notes: Optional[str] = Field(None, description="Notes about this projection")
    creator: ObjectReferenceId = 'doctor.admin'
    created: fd.DefaultDateTime
    last_updated: Optional[datetime.datetime] = None
    
    @model_validator(mode='before')
    def calculate_expected_net(cls, values):
        """Calculate expected net from revenues and expenses."""
        if 'expected_revenues' in values and 'expected_expenses' in values:
            values['expected_net'] = values['expected_revenues'] - values['expected_expenses']
        return values
    
    def update_actuals(self, revenues: Decimal, expenses: Decimal) -> None:
        """Update actual values and calculate variances."""
        self.actual_revenues = revenues
        self.actual_expenses = expenses
        self.actual_net = revenues - expenses
        
        # Calculate variances
        self.variance_revenues = revenues - self.expected_revenues
        self.variance_expenses = expenses - self.expected_expenses
        self.variance_net = self.actual_net - self.expected_net
        
        # Calculate variance percentage
        if self.expected_net != 0:
            self.variance_percentage = float(
                (self.variance_net / abs(self.expected_net)) * 100
            )
        else:
            self.variance_percentage = 0.0 if self.variance_net == 0 else 100.0
        
        self.last_updated = datetime.datetime.now()
    
    def get_accuracy_score(self) -> float:
        """Get projection accuracy score (0-100)."""
        if self.actual_net is None or self.expected_net is None:
            return 0.0
        
        if self.expected_net == 0:
            return 100.0 if self.actual_net == 0 else 0.0
        
        # Calculate accuracy based on how close actual is to expected
        variance_ratio = abs(float(self.variance_net / self.expected_net))
        accuracy = max(0, 100 - (variance_ratio * 100))
        
        return accuracy


class TherapyPackage(MongoModel):
    """Manage therapy session packages for patients."""
    COLLECTION_NAME = 'therapy_packages'
    
    patient_key: ObjectReferenceId = Field(..., description="Patient reference")
    therapist_key: Optional[ObjectReferenceId] = Field(None, description="Assigned therapist")
    
    # Package details
    package_name: str = Field(..., description="Package name/description")
    total_sessions: int = Field(..., description="Total sessions in package")
    sessions_used: int = Field(default=0, description="Sessions already used")
    session_duration_minutes: int = Field(default=50, description="Duration per session")
    
    # Financial details
    price_per_session: Decimal = Field(..., description="Price per session")
    total_amount: Decimal = Field(..., description="Total package amount")
    amount_paid: Decimal = Field(default=Decimal('0'), description="Amount already paid")
    payment_status: PaymentStatus = PaymentStatus.PENDING
    
    # Validity
    purchase_date: fd.DefaultDate
    expiry_date: Optional[datetime.date] = Field(None, description="Package expiry date")
    is_active: bool = Field(True, description="Whether package is active")
    
    # Session tracking
    session_dates: List[datetime.date] = Field(default_factory=list)
    notes: Optional[str] = Field(None, description="Additional notes")
    
    # Metadata
    creator: ObjectReferenceId = 'doctor.admin'
    created: fd.DefaultDateTime
    last_updated: Optional[datetime.datetime] = None
    
    @property
    def sessions_remaining(self) -> int:
        """Calculate remaining sessions."""
        return self.total_sessions - self.sessions_used
    
    @property
    def balance_due(self) -> Decimal:
        """Calculate remaining balance."""
        return self.total_amount - self.amount_paid
    
    def use_session(self, date: Optional[datetime.date] = None) -> bool:
        """Mark a session as used."""
        if self.sessions_remaining <= 0:
            return False
        
        if self.expiry_date and datetime.date.today() > self.expiry_date:
            return False
        
        self.sessions_used += 1
        self.session_dates.append(date or datetime.date.today())
        self.last_updated = datetime.datetime.now()
        
        return True
    
    def add_payment(self, amount: Decimal) -> None:
        """Record a payment."""
        self.amount_paid += amount
        
        # Update payment status
        if self.amount_paid >= self.total_amount:
            self.payment_status = PaymentStatus.PAID
        elif self.amount_paid > 0:
            self.payment_status = PaymentStatus.PARTIAL
        
        self.last_updated = datetime.datetime.now()
    
    def is_expired(self) -> bool:
        """Check if package has expired."""
        if not self.expiry_date:
            return False
        return datetime.date.today() > self.expiry_date