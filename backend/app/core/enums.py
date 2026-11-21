"""
Centralized enum definitions for the application.

Use these instead of raw string literals to ensure consistency
across ORM models, Pydantic schemas, services, and endpoints.
"""

from enum import StrEnum


class LeadStatus(StrEnum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    MEETING_SCHEDULED = "meeting_scheduled"
    CONVERTED = "converted"
    LOST = "lost"
    SPAM = "spam"


class LeadSource(StrEnum):
    META_ADS = "meta_ads"
    MANUAL = "manual"
    REFERRAL = "referral"
    WEBSITE = "website"
    OTHER = "other"


class ConversationStage(StrEnum):
    GREETING = "greeting"
    QUALIFICATION = "qualification"
    DISCOVERY = "discovery"
    PROPOSAL = "proposal"
    DEMO_SCHEDULING = "demo_scheduling"
    FOLLOW_UP = "follow_up"
    CLOSED = "closed"


class MeetingStatus(StrEnum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class ProductStatus(StrEnum):
    ACTIVE = "active"
    BETA = "beta"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class ProductCategory(StrEnum):
    CRM = "crm"
    ANALYTICS = "analytics"
    AUTOMATION = "automation"
    SUPPORT = "support"
    ADD_ON = "add_on"


class BillingPeriod(StrEnum):
    MONTHLY = "monthly"
    ANNUAL = "annual"
    ONE_TIME = "one_time"


class AdminRole(StrEnum):
    ADMIN = "admin"
    AGENT = "agent"


class NotificationType(StrEnum):
    NEW_LEAD = "new_lead"
    LEAD_QUALIFIED = "lead_qualified"
    MEETING_SCHEDULED = "meeting_scheduled"
    ESCALATION = "escalation"
    SYSTEM = "system"


class NotificationChannel(StrEnum):
    IN_APP = "in_app"
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    ALL = "all"
