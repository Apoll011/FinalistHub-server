# Events Management API Documentation

## Setup & Running

This is the backend server for FinalistHub. The frontend client is available at: https://github.com/Apoll011/FinalistHub-client

### Quick Start with Helper Script

**Test Mode** (recommended for development):
```bash
./run.sh --test
```

**Production Mode**:
```bash
./run.sh
```

The helper script handles environment configuration and provides clear information about your mode.

### Docker Compose - Production Mode
Run both server and client with SQLiteCloud database:
```bash
docker-compose up
```
- **Client**: http://localhost:5173 (cloned from GitHub)
- **Server API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Docker Compose - Test Mode
Run with local SQLite database and default admin user (username: `admin`, password: `admin`):
```bash
docker-compose --env-file .env.test up
```
- **Client**: http://localhost:5173
- **Server API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Default Admin**: username=`admin`, password=`admin`

### Local Development
```bash
cp .env.example .env
pip install -r requirements.txt
python init_db.py
uvicorn main:app --reload
```

---

## 1. Events

### 1.1 Create Events (Admin Only)

#### `POST /events`<!-- {"fold":true} -->
Create a new event.

**Request Body:**
```json
{
  "name": "string",
  "date": "YYYY-MM-DD",
  "time": "HH:mm",
  "location": "string",
  "description": "string"
}
```

**Response:** (201 Created)
```json
{
  "id": "string",
  "name": "string",
  "date": "YYYY-MM-DD",
  "time": "HH:mm",
  "location": "string",
  "description": "string",
  "status": "active",
  "createdAt": "YYYY-MM-DDTHH:mm:ssZ"
}
```

#### `POST /events/{eventId}/tickets`<!-- {"fold":true} -->
Add tickets to an event.

**Request Body:**
```json
{
  "type": "string",
  "price": "number"
}
```

**Response:** (201 Created)
```json
{
  "id": "string",
  "eventId": "string",
  "type": "string",
  "price": "number",
  "available": true,
  "createdAt": "YYYY-MM-DDTHH:mm:ssZ"
}
```

#### `POST /events/{eventId}/items`<!-- {"fold":true} -->
Add items to be sold at an event.

**Request Body:**
```json
{
  "name": "string",
  "quantity": "number",
  "price": "number"
}
```

**Response:** (201 Created)
```json
{
  "id": "string",
  "eventId": "string",
  "name": "string",
  "quantity": "number",
  "price": "number",
  "createdAt": "YYYY-MM-DDTHH:mm:ssZ"
}
```

### 1.2 Sales Mode (Members)

#### `POST /sales/stock-items`<!-- {"fold":true} -->
Sell an item from stock and add the revenue.

**Request Body:**
```json
{
  "itemId": "string",
  "quantitySold": "number"
}
```

**Response:** (200 OK)
```json
{
  "id": "string",
  "itemId": "string",
  "quantitySold": "number",
  "totalRevenue": "number",
  "timestamp": "YYYY-MM-DDTHH:mm:ssZ"
}
```

#### `POST /sales/custom-item`<!-- {"fold":true} -->
Sell an item that wasn't previously created.

**Request Body:**
```json
{
  "name": "string",
  "price": "number",
  "quantitySold": "number"
}
```

**Response:** (200 OK)
```json
{
  "id": "string",
  "name": "string",
  "price": "number",
  "quantitySold": "number",
  "totalRevenue": "number",
  "timestamp": "YYYY-MM-DDTHH:mm:ssZ"
}
```

#### `POST /sales/register-item`<!-- {"fold":true} -->
Register a new item.

**Request Body:**
```json
{
  "name": "string",
  "quantity": "number",
  "price": "number"
}
```

**Response:** (201 Created)
```json
{
  "id": "string",
  "name": "string",
  "quantity": "number",
  "price": "number",
  "createdAt": "YYYY-MM-DDTHH:mm:ssZ"
}
```

#### `GET /sales/receipt/{eventId}`<!-- {"fold":true} -->
Generate and print a receipt for all sales made during a specific event.

**Response:** (200 OK)
```json
{
  "eventId": "string",
  "totalSales": "number",
  "itemsSold": [
    {
      "name": "string",
      "quantity": "number",
      "unitPrice": "number",
      "totalPrice": "number"
    }
  ],
  "timestamp": "YYYY-MM-DDTHH:mm:ssZ"
}
```

### 1.3 Monitor Events (Members)

#### `GET /events/calendar`<!-- {"fold":true} -->
View all events on a calendar.

**Response:** (200 OK)
```json
{
  "events": [
    {
      "id": "string",
      "name": "string",
      "date": "YYYY-MM-DD",
      "time": "HH:mm",
      "location": "string",
      "status": "string"
    }
  ]
}
```

#### `PATCH /events/{eventId}/cancel`<!-- {"fold":true} -->
Cancel an event.

**Response:** (200 OK)
```json
{
  "id": "string",
  "status": "cancelled",
  "cancelledAt": "YYYY-MM-DDTHH:mm:ssZ"
}
```

#### `PATCH /events/{eventId}/reschedule`<!-- {"fold":true} -->
Reschedule an event.

**Request Body:**
```json
{
  "date": "YYYY-MM-DD",
  "time": "HH:mm"
}
```

**Response:** (200 OK)
```json
{
  "id": "string",
  "date": "YYYY-MM-DD",
  "time": "HH:mm",
  "updatedAt": "YYYY-MM-DDTHH:mm:ssZ"
}
```

#### `GET /events/{eventId}/details`<!-- {"fold":true} -->
View details of a past event, including sales, observations, and edits.

**Response:** (200 OK)
```json
{
  "id": "string",
  "name": "string",
  "date": "YYYY-MM-DD",
  "time": "HH:mm",
  "location": "string",
  "status": "string",
  "sales": {
    "totalRevenue": "number",
    "itemsSold": [
      {
        "name": "string",
        "quantity": "number",
        "revenue": "number"
      }
    ]
  },
  "observations": [
    {
      "content": "string",
      "timestamp": "YYYY-MM-DDTHH:mm:ssZ"
    }
  ],
  "edits": [
    {
      "field": "string",
      "oldValue": "string",
      "newValue": "string",
      "timestamp": "YYYY-MM-DDTHH:mm:ssZ"
    }
  ]
}
```

#### `POST /events/{eventId}/observations`<!-- {"fold":true} -->
Add or edit observations for an event.

**Request Body:**
```json
{
  "content": "string"
}
```

**Response:** (201 Created)
```json
{
  "id": "string",
  "eventId": "string",
  "content": "string",
  "createdAt": "YYYY-MM-DDTHH:mm:ssZ"
}
```

## 2. Financial Monitoring

### 2.1 Manage Financial Account (Admin Only)

#### `POST /finance/revenue`<!-- {"fold":true} -->
Add revenue to the financial account.

**Request Body:**
```json
{
  "description": "string",
  "amount": "number"
}
```

**Response:** (201 Created)
```json
{
  "id": "string",
  "type": "revenue",
  "description": "string",
  "amount": "number",
  "timestamp": "YYYY-MM-DDTHH:mm:ssZ"
}
```

#### `POST /finance/expense`<!-- {"fold":true} -->
Add an expense to the financial account.

**Request Body:**
```json
{
  "description": "string",
  "amount": "number"
}
```

**Response:** (201 Created)
```json
{
  "id": "string",
  "type": "expense",
  "description": "string",
  "amount": "number",
  "timestamp": "YYYY-MM-DDTHH:mm:ssZ"
}
```

#### `GET /finance/balance`<!-- {"fold":true} -->
View the current account balance.

**Response:** (200 OK)
```json
{
  "currentBalance": "number",
  "lastUpdated": "YYYY-MM-DDTHH:mm:ssZ"
}
```

#### `GET /finance/transactions`<!-- {"fold":true} -->
View a detailed list of all transactions.

**Response:** (200 OK)
```json
{
  "transactions": [
    {
      "id": "string",
      "type": "string",
      "description": "string",
      "amount": "number",
      "timestamp": "YYYY-MM-DDTHH:mm:ssZ"
    }
  ]
}
```

#### `GET /finance/transactions/monthly`<!-- {"fold":true} -->
View monthly financial reports.

**Response:** (200 OK)
```json
{
  "month": "YYYY-MM",
  "totalRevenue": "number",
  "totalExpenses": "number",
  "netIncome": "number",
  "transactions": [
    {
      "id": "string",
      "type": "string",
      "description": "string",
      "amount": "number",
      "timestamp": "YYYY-MM-DDTHH:mm:ssZ"
    }
  ]
}
```

## 3. Committee Meetings

### 3.1 Manage Meetings (Admin Only)

#### `POST /meetings`<!-- {"fold":true} -->
Create a new meeting.

**Request Body:**
```json
{
  "date": "YYYY-MM-DD",
  "time": "HH:mm",
  "location": "string",
  "agenda": "string"
}
```

**Response:** (201 Created)
```json
{
  "id": "string",
  "date": "YYYY-MM-DD",
  "time": "HH:mm",
  "location": "string",
  "agenda": "string",
  "status": "scheduled",
  "createdAt": "YYYY-MM-DDTHH:mm:ssZ"
}
```

#### `PATCH /meetings/{meetingId}`<!-- {"fold":true} -->
Edit or reschedule a meeting.

**Request Body:**
```json
{
  "date": "YYYY-MM-DD",
  "time": "HH:mm",
  "agenda": "string"
}
```

**Response:** (200 OK)
```json
{
  "id": "string",
  "date": "YYYY-MM-DD",
  "time": "HH:mm",
  "agenda": "string",
  "updatedAt": "YYYY-MM-DDTHH:mm:ssZ"
}
```

#### `DELETE /meetings/{meetingId}`<!-- {"fold":true} -->
Cancel a meeting.

**Response:** (204 No Content)

#### `POST /meetings/{meetingId}/minutes`<!-- {"fold":true} -->
Add meeting minutes as a Word document.

**Request Body:**
```
Content-Type: multipart/form-data
file: [Word Document Binary]
```

**Response:** (201 Created)
```json
{
  "id": "string",
  "meetingId": "string",
  "fileName": "string",
  "fileSize": "number",
  "uploadedAt": "YYYY-MM-DDTHH:mm:ssZ"
}
```

### 3.2 View Meetings (Members)

#### `GET /meetings/upcoming`<!-- {"fold":true} -->
View upcoming meetings.

**Response:** (200 OK)
```json
{
  "meetings": [
    {
      "id": "string",
      "date": "YYYY-MM-DD",
      "time": "HH:mm",
      "location": "string",
      "agenda": "string",
      "status": "string"
    }
  ]
}
```

#### `GET /meetings/{meetingId}/minutes`<!-- {"fold":true} -->
View meeting minutes.

**Response:** (200 OK)
```
Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document
[Word Document Binary]
```
