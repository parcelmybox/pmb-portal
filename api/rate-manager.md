Here’s a design doc that outlines your requirements for a Django backend using MariaDB, including data modeling, API endpoints, and a simple CRUD UI.

---

## 📦 **Shipping Rates Management Backend – Design Document**

### 🎯 **Objective**

Build a Django-based backend with MariaDB to manage shipping rates. Support POST for creating/updating rates and GET for retrieving with filters. Include a simple CRUD interface for admin users.

---

### 🗄️ **Database Schema**

**Table: `shipping_rates`**

| Column Name          | Type          | Description                                      |
| -------------------- | ------------- | ------------------------------------------------ |
| id                   | AutoField     | Primary Key                                      |
| package\_type        | CharField     | One of: 'medical', 'document', 'package'         |
| carrier              | CharField     | One of: 'SFL', 'DHL', 'ATLANTIC', 'FEDEX', 'UPS' |
| source\_city         | CharField     | City name (e.g., Hyderabad)                      |
| destination\_country | CharField     | Country name (e.g., USA)                         |
| price                | DecimalField  | Shipping price                                   |
| currency             | CharField     | Currency code (e.g., INR, USD)                   |
| weight               | DecimalField  | Weight of the package                            |
| weight\_unit         | CharField     | One of: 'KG', 'LB'                               |
| created\_at          | DateTimeField | Auto timestamp                                   |
| updated\_at          | DateTimeField | Auto timestamp                                   |

---

### 🔌 **API Design**

#### 1. `POST /api/rates/`

Create or update a shipping rate.

**Request Body Example:**

```json
{
  "package_type": "medicine",
  "carrier": "DHL",
  "source_city": "Hyderabad",
  "destination_country": "USA",
  "price": 2800,
  "currency": "INR",
  "weight": 0.5,
  "weight_unit": "KG"
}
```

* If an identical entry exists (same package type, carrier, source city, destination country, weight, and unit), update the price.
* Else, create a new record.

**Response Example:**

```json
{
  "status": "success",
  "message": "Rate saved successfully."
}
```

---

#### 2. `GET /api/rates/`

Retrieve shipping rates with optional filters.

**Query Parameters (optional):**

* `package_type`
* `carrier`
* `source_city`
* `destination_country`
* `currency`
* `weight_unit`

**Example:**
`GET /api/rates/?carrier=DHL&destination_country=USA`

**Response:**

```json
[
  {
    "package_type": "medicine",
    "carrier": "DHL",
    "source_city": "Hyderabad",
    "destination_country": "USA",
    "price": 2800,
    "currency": "INR",
    "weight": 0.5,
    "weight_unit": "KG"
  },
  ...
]
```

---

### 🖥️ **Admin CRUD Interface**

Use Django Admin or Django Generic Views to implement:

* List all rates
* Add a new rate
* Edit existing rate
* Delete rate

Optional: Add search & filter options by carrier, source, destination.

---

### 🏗️ **Django App Structure (Simplified)**

```
shipping_rates/
├── models.py
├── views.py
├── serializers.py
├── urls.py
├── admin.py
├── templates/
│   └── (optional UI)
```

