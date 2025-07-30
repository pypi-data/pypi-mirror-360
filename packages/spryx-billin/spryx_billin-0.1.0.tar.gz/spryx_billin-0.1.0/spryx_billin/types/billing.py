from enum import StrEnum


class BalanceType(StrEnum):
    """Type of balance."""
    PLAN = "PLAN"
    PROMOTION = "PROMOTION"
    CUSTOMER_SERVICE = "CUSTOMER_SERVICE"
    MANUAL = "MANUAL"


class CreditAdjustmentType(StrEnum):
    """Type of credit adjustment."""
    REFUND = "REFUND"
    PROMOTION = "PROMOTION"
    CORRECTION = "CORRECTION"
    MANUAL = "MANUAL"
    OTHER = "OTHER"


class CreditPricingStatus(StrEnum):
    """Status of credit pricing rules for versioning and immutability."""
    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"
    INACTIVE = "INACTIVE"


class FeatureType(StrEnum):
    """Types of features available in plans."""
    LIMIT = "LIMIT"
    BOOLEAN = "BOOLEAN"
    TEXT = "TEXT"
    QUOTA = "QUOTA"


class Currency(StrEnum):
    """Supported currencies."""
    BRL = "BRL"
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    CAD = "CAD"
    AUD = "AUD"
    JPY = "JPY"


class PaymentProvider(StrEnum):
    """Supported payment providers."""
    STRIPE = "STRIPE"
    MERCADOPAGO = "MERCADOPAGO"
    PAGSEGURO = "PAGSEGURO"


class PlanStatus(StrEnum):
    """Status de um plano."""
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    DEPRECATED = "DEPRECATED"
    ARCHIVED = "ARCHIVED"


class RecurringInterval(StrEnum):
    """Billing intervals for recurring subscriptions."""
    MONTH = "MONTH"
    YEAR = "YEAR"
    WEEK = "WEEK"
    DAY = "DAY"


class SubscriptionStatus(StrEnum):
    """Status of a subscription."""
    INCOMPLETE = "INCOMPLETE"
    INCOMPLETE_EXPIRED = "INCOMPLETE_EXPIRED"
    TRIALING = "TRIALING"
    ACTIVE = "ACTIVE"
    PAST_DUE = "PAST_DUE"
    CANCELED = "CANCELED"
    UNPAID = "UNPAID"
    PAUSED = "PAUSED"


class CollectionMethod(StrEnum):
    """Methods for collecting payments."""
    CHARGE_AUTOMATICALLY = "CHARGE_AUTOMATICALLY"
    SEND_INVOICE = "SEND_INVOICE" 