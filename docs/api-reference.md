# API Reference

Base URL: `http://localhost:8000/api/v1`

Auth header: `Authorization: Bearer <jwt_token>`

Error response format:
```json
{
  "detail": "Error message describing the problem"
}
```

All endpoints that require auth respond with `401 Unauthorized` if the token is missing, expired, or invalid. `403 Forbidden` if the user lacks the required role.

---

## Auth — `/api/v1/auth`

No auth required (except `/me`).

### `POST /auth/signup`

Register a new admin user.

**Request:**
```json
{
  "email": "admin@example.com",
  "password": "securePassword123",
  "name": "Admin Name"
}
```

**Response `201 Created`:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "admin@example.com",
  "name": "Admin Name",
  "role": "admin",
  "created_at": "2026-05-10T10:00:00+00:00"
}
```

**Errors:** `409 Conflict` if email already registered.

### `POST /auth/login`

Authenticate and receive JWT tokens.

**Request:**
```json
{
  "email": "admin@example.com",
  "password": "securePassword123"
}
```

**Response `200 OK`:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "admin@example.com",
    "name": "Admin Name",
    "role": "admin"
  }
}
```

**Errors:** `401 Unauthorized` if credentials are invalid.

### `GET /auth/me`

Get current user profile. **Auth required.**

**Response `200 OK`:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "admin@example.com",
  "name": "Admin Name",
  "role": "admin"
}
```

### `POST /auth/refresh`

Exchange a refresh token for new access and refresh tokens.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response `200 OK`:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

**Errors:** `401 Unauthorized` if refresh token is invalid or expired.

### `POST /auth/logout`

Invalidate current session. **Auth required.**

**Response `200 OK`:**
```json
{
  "message": "Logged out successfully"
}
```

### `POST /auth/change-password`

Change password for authenticated user. **Auth required.**

**Request:**
```json
{
  "current_password": "oldPassword123",
  "new_password": "newSecurePassword456"
}
```

**Response `200 OK`:**
```json
{
  "message": "Password changed successfully"
}
```

**Errors:** `400 Bad Request` if current password is wrong.

### `POST /auth/reset-password`

Request a password reset email. No auth required.

**Request:**
```json
{
  "email": "admin@example.com"
}
```

**Response `200 OK`:**
```json
{
  "message": "Password reset email sent if account exists",
  "reset_token": "eyJhbGciOiJIUzI1NiIs..." // Only in dev mode
}
```

### `POST /auth/reset-password/confirm`

Complete password reset with token from email.

**Request:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "new_password": "newSecurePassword789"
}
```

**Response `200 OK`:**
```json
{
  "message": "Password reset successfully"
}
```

**Errors:** `400 Bad Request` if token is invalid or expired.

---

## Leads — `/api/v1/leads`

Auth required (any authenticated user).

### `GET /leads`

Paginated list of leads with optional filters.

**Query Parameters:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `page` | int | 1 | Page number |
| `page_size` | int | 20 | Items per page (max 100) |
| `status` | string | — | Filter by status: `new`, `contacted`, `qualified`, `meeting_scheduled`, `converted`, `lost`, `spam` |
| `source` | string | — | Filter by source: `meta_ads`, `manual`, `referral`, `website`, `other` |
| `search` | string | — | Search by name, phone, or email (partial match) |

**Response `200 OK`:**
```json
{
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "whatsapp_phone": "+971501234567",
      "name": "Rahul Sharma",
      "email": "rahul@example.com",
      "status": "new",
      "source": "meta_ads",
      "conversation_stage": "information_gathering",
      "budget_min": 1500000.00,
      "budget_max": 2500000.00,
      "property_type": "apartment",
      "bedrooms_min": 2,
      "location": "Dubai Marina",
      "notes": null,
      "assigned_to": null,
      "extra_data": {},
      "last_contacted_at": "2026-05-10T10:30:00+00:00",
      "created_at": "2026-05-10T10:00:00+00:00",
      "updated_at": "2026-05-10T10:30:00+00:00"
    }
  ],
  "total": 42,
  "page": 1,
  "page_size": 20,
  "total_pages": 3
}
```

### `GET /leads/{lead_id}`

Get a single lead with full details.

**Path Parameters:** `lead_id` (UUID)

**Response `200 OK`:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "whatsapp_phone": "+971501234567",
  "name": "Rahul Sharma",
  "email": "rahul@example.com",
  "status": "new",
  "source": "meta_ads",
  "conversation_stage": "information_gathering",
  "budget_min": 1500000.00,
  "budget_max": 2500000.00,
  "property_type": "apartment",
  "bedrooms_min": 2,
  "location": "Dubai Marina",
  "notes": null,
  "assigned_to": null,
  "extra_data": {},
  "last_contacted_at": "2026-05-10T10:30:00+00:00",
  "created_at": "2026-05-10T10:00:00+00:00",
  "updated_at": "2026-05-10T10:30:00+00:00"
}
```

**Errors:** `404 Not Found`

### `POST /leads`

Create a lead manually (from dashboard).

**Request:**
```json
{
  "whatsapp_phone": "+971501234567",
  "name": "Rahul Sharma",
  "email": "rahul@example.com",
  "status": "new",
  "source": "manual",
  "budget_min": 1500000.00,
  "budget_max": 2500000.00,
  "property_type": "apartment",
  "bedrooms_min": 2,
  "location": "Dubai Marina",
  "notes": "Called from office"
}
```

**Response `201 Created`:** Full `LeadResponse` object.

**Errors:** `409 Conflict` if phone already exists.

### `PATCH /leads/{lead_id}`

Update any subset of lead fields.

**Request** (any combination of fields):
```json
{
  "status": "qualified",
  "notes": "Interested in Marina 2BR under 2.5M AED",
  "budget_max": 2500000.00
}
```

**To clear a field**, pass `null`:
```json
{
  "budget_max": null,
  "location": null
}
```

**Response `200 OK`:** Updated `LeadResponse` object.

**Errors:** `404 Not Found`

### `DELETE /leads/{lead_id}`

Delete a lead and all related conversations and meetings (CASCADE).

**Response `204 No Content`**

**Errors:** `404 Not Found`

### `GET /leads/{lead_id}/conversations`

Get message history for a lead.

**Response `200 OK`:**
```json
[
  {
    "id": "660e8400-e29b-41d4-a716-446655440010",
    "role": "user",
    "content": "Hi, I'm looking for a 2BR in Dubai Marina",
    "message_type": "text",
    "created_at": "2026-05-10T10:00:00+00:00"
  },
  {
    "id": "660e8400-e29b-41d4-a716-446655440011",
    "role": "assistant",
    "content": "Hello Rahul! Welcome to LeadGen Realty. I'd be happy to help you find a 2BR in Dubai Marina. Do you have a budget range in mind?",
    "message_type": "text",
    "created_at": "2026-05-10T10:00:05+00:00"
  }
]
```

### `POST /leads/{lead_id}/notes`

Add an internal note to a lead.

**Request:**
```json
{
  "content": "Called lead — interested in a site visit next week"
}
```

**Response `200 OK`:**
```json
{
  "message": "Note added",
  "lead_id": "550e8400-e29b-41d4-a716-446655440001"
}
```

---

## Properties — `/api/v1/properties`

Auth required.

### `GET /properties`

Paginated list with search and filters.

**Query Parameters:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `page` | int | 1 | Page number |
| `page_size` | int | 20 | Items per page (max 100) |
| `type` | string | — | `apartment`, `villa`, `townhouse`, `penthouse`, `studio` |
| `location` | string | — | Partial match on location |
| `min_price` | number | — | Minimum price in AED |
| `max_price` | number | — | Maximum price in AED |
| `bedrooms` | int | — | Minimum bedrooms |
| `status` | string | — | `available`, `sold`, `rented`, `under_offer`, `archived` |
| `search` | string | — | Search title and description |

**Response `200 OK`:**
```json
{
  "data": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440020",
      "title": "2BR Luxury Apartment in Dubai Marina",
      "description": "Stunning marina view with full amenities...",
      "price": 2500000.00,
      "property_type": "apartment",
      "bedrooms": 2,
      "bathrooms": 2,
      "area_sqft": 1200.0,
      "location": "Dubai Marina",
      "latitude": 25.0799,
      "longitude": 55.1403,
      "amenities": ["pool", "gym", "parking", "concierge"],
      "images": [
        {"url": "https://...", "alt": "Living room", "order": 1},
        {"url": "https://...", "alt": "Bedroom", "order": 2}
      ],
      "featured": true,
      "status": "available",
      "extra_data": {"developer": "Emaar", "completion_year": 2024},
      "created_at": "2026-05-01T00:00:00+00:00",
      "updated_at": "2026-05-01T00:00:00+00:00"
    }
  ],
  "total": 20,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

### `GET /properties/{property_id}`

Get a single property.

**Response `200 OK`:** Full `PropertyResponse` object.

**Errors:** `404 Not Found`

### `POST /properties`

Create a new property listing.

**Request:**
```json
{
  "title": "2BR Luxury Apartment in Dubai Marina",
  "description": "Stunning marina view with full amenities...",
  "price": 2500000.00,
  "property_type": "apartment",
  "bedrooms": 2,
  "bathrooms": 2,
  "area_sqft": 1200.0,
  "location": "Dubai Marina",
  "latitude": 25.0799,
  "longitude": 55.1403,
  "amenities": ["pool", "gym", "parking"],
  "images": [{"url": "https://...", "alt": "Living room", "order": 1}],
  "featured": false,
  "status": "available",
  "extra_data": {}
}
```

**Response `201 Created`:** Full `PropertyResponse` object.

### `PUT /properties/{property_id}`

Full update of a property (all fields required).

**Request:** Same schema as POST.

**Response `200 OK`:** Updated `PropertyResponse`.

**Errors:** `404 Not Found`

### `DELETE /properties/{property_id}`

Soft delete — sets status to `archived`.

**Response `204 No Content`**

**Errors:** `404 Not Found`

### `PATCH /properties/{property_id}/featured`

Toggle featured status.

**Request:**
```json
{
  "featured": true
}
```

**Response `200 OK`:**
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440020",
  "featured": true,
  "message": "Featured status updated"
}
```

---

## Meetings — `/api/v1/meetings`

Auth required.

### `GET /meetings`

Paginated list with optional status filter.

**Query Parameters:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `page` | int | 1 | Page number |
| `page_size` | int | 20 | Items per page |
| `status` | string | — | `scheduled`, `confirmed`, `completed`, `cancelled`, `no_show` |

**Response `200 OK`:**
```json
{
  "data": [
    {
      "id": "880e8400-e29b-41d4-a716-446655440030",
      "lead_id": "550e8400-e29b-41d4-a716-446655440001",
      "scheduled_at": "2026-05-15T10:00:00+04:00",
      "duration_minutes": 30,
      "timezone": "Asia/Dubai",
      "google_event_id": null,
      "meet_link": null,
      "status": "scheduled",
      "notes": "Show 2BR in Dubai Marina",
      "created_at": "2026-05-10T10:30:00+00:00",
      "updated_at": "2026-05-10T10:30:00+00:00"
    }
  ],
  "total": 5,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

### `GET /meetings/upcoming`

Get next 5 upcoming meetings (for dashboard widget).

**Response `200 OK`:**
```json
{
  "data": [
    {
      "id": "880e8400-...",
      "lead_id": "550e8400-...",
      "lead_name": "Rahul Sharma",
      "lead_phone": "+971501234567",
      "scheduled_at": "2026-05-15T10:00:00+04:00",
      "duration_minutes": 30,
      "status": "scheduled"
    }
  ],
  "total": 5
}
```

### `GET /meetings/{meeting_id}`

Get a single meeting.

**Errors:** `404 Not Found`

### `POST /meetings`

Schedule a new meeting.

**Request:**
```json
{
  "lead_id": "550e8400-e29b-41d4-a716-446655440001",
  "scheduled_at": "2026-05-15T10:00:00",
  "duration_minutes": 30,
  "timezone": "Asia/Dubai",
  "notes": "Show 2BR in Dubai Marina"
}
```

**Response `201 Created`:** Full `MeetingResponse`.

### `PATCH /meetings/{meeting_id}`

Update or reschedule a meeting.

**Request:**
```json
{
  "scheduled_at": "2026-05-16T14:00:00",
  "status": "rescheduled",
  "notes": "Rescheduled — client preferred afternoon"
}
```

**Response `200 OK`:** Updated `MeetingResponse`.

**Errors:** `404 Not Found`

### `DELETE /meetings/{meeting_id}`

Cancel a meeting (sets status to `cancelled`).

**Response `204 No Content`**

---

## Analytics — `/api/v1/analytics`

Auth required.

### `GET /analytics/overview`

Dashboard summary statistics.

**Response `200 OK`:**
```json
{
  "total_leads": 150,
  "qualified_leads": 45,
  "upcoming_meetings": 8,
  "converted": 12,
  "conversion_rate": 8.0,
  "leads_today": 3,
  "meetings_this_week": 5
}
```

### `GET /analytics/leads-over-time?days=30`

Daily lead acquisition counts.

**Response `200 OK`:**
```json
{
  "data": [
    {"date": "2026-04-10", "count": 5},
    {"date": "2026-04-11", "count": 3},
    {"date": "2026-04-12", "count": 7}
  ],
  "total": 150,
  "days": 30
}
```

### `GET /analytics/status-breakdown`

Lead distribution by status.

**Response `200 OK`:**
```json
{
  "data": [
    {"status": "new", "count": 60, "percentage": 40.0},
    {"status": "contacted", "count": 30, "percentage": 20.0},
    {"status": "qualified", "count": 25, "percentage": 16.7},
    {"status": "meeting_scheduled", "count": 15, "percentage": 10.0},
    {"status": "converted", "count": 12, "percentage": 8.0},
    {"status": "lost", "count": 5, "percentage": 3.3},
    {"status": "spam", "count": 3, "percentage": 2.0}
  ]
}
```

### `GET /analytics/source-breakdown`

Lead distribution by source.

**Response `200 OK`:**
```json
{
  "data": [
    {"source": "meta_ads", "count": 100, "percentage": 66.7},
    {"source": "referral", "count": 25, "percentage": 16.7},
    {"source": "website", "count": 15, "percentage": 10.0},
    {"source": "manual", "count": 10, "percentage": 6.7}
  ]
}
```

---

## WhatsApp Webhook — `/api/v1/whatsapp`

No auth required. Uses signature verification instead.

### `GET /whatsapp/webhook`

Meta platform verification handshake. Called by Meta when setting up the webhook.

**Query Parameters:**

| Param | Type | Description |
|-------|------|-------------|
| `hub.mode` | string | Should be `subscribe` |
| `hub.verify_token` | string | Should match `WHATSAPP_VERIFY_TOKEN` env var |
| `hub.challenge` | string | Echoed back on success |

**Response `200 OK`:**
```
<challenge_string>
```

**Errors:** `403 Forbidden` if verify token doesn't match.

### `POST /whatsapp/webhook`

Inbound WhatsApp message handler.

**Headers:**
- `X-Hub-Signature-256`: HMAC-SHA256 signature of body (verified against `WHATSAPP_APP_SECRET`)
- `Content-Type: application/json`

**Request body** (Meta webhook payload):
```json
{
  "object": "whatsapp_business_account",
  "entry": [
    {
      "id": "123456789",
      "changes": [
        {
          "value": {
            "messaging_product": "whatsapp",
            "metadata": {
              "display_phone_number": "15551234567",
              "phone_number_id": "123456789"
            },
            "contacts": [
              {
                "profile": {"name": "Rahul"},
                "wa_id": "971501234567"
              }
            ],
            "messages": [
              {
                "from": "971501234567",
                "id": "wamid.HBgN..."
              }
            ]
          },
          "field": "messages"
        }
      ]
    }
  ]
}
```

**Processing pipeline:**
1. Verify `X-Hub-Signature-256` (skip if `WHATSAPP_APP_SECRET` is empty)
2. Parse sender phone + message text + message ID
3. Dedup by message ID (check `conversations.whatsapp_message_id`)
4. Get or create lead by phone with source=`meta_ads`
5. Store user message in `conversations` table
6. Call `process_message()` — AI agent generates response
7. Send response via WhatsApp Meta Cloud API
8. Store assistant response in `conversations` table
9. Return acknowledgment

**Response `200 OK`:**
```json
{
  "status": "ok"
}
```

This endpoint always returns 200. Errors are logged and the lead receives a fallback message when the agent fails.

---

## System

### `GET /health`

No auth required.

**Response `200 OK`:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "environment": "development"
}
```

## HTTP Status Code Reference

| Code | Meaning | Common Uses |
|------|---------|-------------|
| `200` | OK | Successful GET, PATCH, PUT |
| `201` | Created | Successful POST (resource created) |
| `204` | No Content | Successful DELETE |
| `400` | Bad Request | Invalid input, validation error |
| `401` | Unauthorized | Missing/invalid/expired auth token |
| `403` | Forbidden | Insufficient role permissions |
| `404` | Not Found | Resource doesn't exist |
| `409` | Conflict | Duplicate (email, phone already exists) |
| `422` | Unprocessable Entity | Request body fails Pydantic validation |
| `429` | Too Many Requests | Rate limit exceeded |
| `500` | Internal Server Error | Unhandled exception |
| `502` | Bad Gateway | External service error (Groq, WhatsApp, etc.) |
