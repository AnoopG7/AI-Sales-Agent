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
    INFORMATION_GATHERING = "information_gathering"
    PROPERTY_SEARCH = "property_search"
    PROPERTY_PRESENTATION = "property_presentation"
    SCHEDULING = "scheduling"
    FOLLOW_UP = "follow_up"
    CLOSED = "closed"


class MeetingStatus(StrEnum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class PropertyStatus(StrEnum):
    AVAILABLE = "available"
    SOLD = "sold"
    RENTED = "rented"
    UNDER_OFFER = "under_offer"
    ARCHIVED = "archived"


class PropertyType(StrEnum):
    APARTMENT = "apartment"
    VILLA = "villa"
    TOWNHOUSE = "townhouse"
    PENTHOUSE = "penthouse"
    STUDIO = "studio"


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
