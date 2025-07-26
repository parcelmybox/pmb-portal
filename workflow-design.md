📦 End-to-End Customer Shipping Workflow
1️⃣ Customer Enquiry
🔍 Customer contacts support to learn about services.

2️⃣ Profile Registration
📝 Customer registers and creates a profile.

3️⃣ Pickup Request
📦 Customer places a pickup request through app/portal/phone.

4️⃣ Package Collection
🚚 Operations team schedules and collects the package.

5️⃣ Boxing & Quotation
📦 Package is weighed and boxed.
📄 Quotation shared with:

Carrier options

Estimated delivery time

Shipping cost

6️⃣ Customer Confirms Carrier & Price
✅ Customer selects preferred carrier/price/timeline.

7️⃣ Invoice Generation
🧾 Operations team generates and shares invoice.

8️⃣ Customer Payment
💳 Customer pays via preferred payment method.

9️⃣ Document Collection
📄 Operations team collects:

Sender’s Aadhaar & KYC docs

Receiver’s address & phone number

🔟 Dispatch to Carrier
🚚 Package is handed over to the chosen carrier.

1️⃣1️⃣ Tracking Number Issued
📦 Carrier shares tracking number with operations.

1️⃣2️⃣ Tracking Shared with Customer
📩 Operations forwards tracking number to customer.

1️⃣3️⃣ Feedback Form Shared
📄 Customer receives a feedback form including tracking details.

1️⃣4️⃣ Feedback Received
✍️ Customer submits feedback on service experience

Here's a **relational database schema** design to support the end-to-end shipping workflow you outlined. It uses normalized tables for clarity and future scalability.

---

### 🧩 **Database Schema for Shipping Workflow**

#### **1. `users`**

Stores customer profiles.

```sql
user_id (PK)  
name  
email  
phone  
address  
aadhaar_number  
created_at  
```

---

#### **2. `pickup_requests`**

Stores pickup requests by users.

```sql
pickup_id (PK)  
user_id (FK → users.user_id)  
requested_date  
pickup_address  
pickup_status  -- Pending, Picked, Cancelled  
notes  
created_at  
```

---

#### **3. `packages`**

Each pickup request may include one or more packages.

```sql
package_id (PK)  
pickup_id (FK → pickup_requests.pickup_id)  
weight  
dimensions  
contents_description  
packaging_status  -- Boxed, Loose, Fragile  
created_at  
```

---

#### **4. `carrier_quotes`**

Stores multiple shipping quotes per package.

```sql
quote_id (PK)  
package_id (FK → packages.package_id)  
carrier_name  
estimated_days  
price  
quote_status -- Sent, Selected, Expired  
created_at  
```

---

#### **5. `invoices`**

Generated once the user selects a quote.

```sql
invoice_id (PK)  
quote_id (FK → carrier_quotes.quote_id)  
invoice_number  
amount  
status  -- Pending, Paid, Failed  
issued_at  
paid_at  
```

---

#### **6. `shipment_docs`**

Stores sender/receiver documents and shipping data.

```sql
shipment_id (PK)  
invoice_id (FK → invoices.invoice_id)  
sender_aadhaar  
receiver_name  
receiver_phone  
receiver_address  
documents_uploaded (Boolean)  
created_at  
```

---

#### **7. `dispatches`**

Tracking the handoff to carrier and tracking number.

```sql
dispatch_id (PK)  
shipment_id (FK → shipment_docs.shipment_id)  
carrier_name  
dispatch_date  
tracking_number  
tracking_status -- Active, Delivered, Delayed  
created_at  
```

---

#### **8. `feedback`**

Feedback tied to tracking number.

```sql
feedback_id (PK)  
dispatch_id (FK → dispatches.dispatch_id)  
user_id (FK → users.user_id)  
rating (1-5)  
comments  
submitted_at  
```

---

### 🔗 **Schema Relationships Summary**

* One **user** can have many **pickup\_requests**.
* One **pickup\_request** can have multiple **packages**.
* Each **package** can have multiple **carrier\_quotes**.
* One **selected quote** leads to an **invoice**.
* Each **invoice** is linked to **shipment\_docs** (sender/receiver info).
* One **shipment** results in a **dispatch** with tracking info.
* One **dispatch** allows a **feedback** entry.


Here’s a clean and modular **RESTful API endpoint design** for the shipping workflow schema we defined. These endpoints follow standard naming conventions and map directly to each table and workflow stage.

---

### 🚀 **Shipping Workflow – REST API Endpoints**

---

### 🔐 **Authentication**

```http
POST   /api/register              # Register new customer
POST   /api/login                 # Login and return JWT token
GET    /api/profile               # View user profile (auth required)
PUT    /api/profile               # Update user profile
```

---

### 📦 **Pickup Requests**

```http
POST   /api/pickups/              # Create a new pickup request
GET    /api/pickups/              # List all pickup requests (user-specific or admin)
GET    /api/pickups/{pickup_id}/  # View single pickup request
PUT    /api/pickups/{pickup_id}/  # Update pickup (e.g., status)
```

---

### 📬 **Packages**

```http
POST   /api/packages/             # Add a package to a pickup request
GET    /api/packages/?pickup_id=  # Get all packages for a pickup
GET    /api/packages/{id}/        # Get specific package
PUT    /api/packages/{id}/        # Update package details
```

---

### 💰 **Carrier Quotes**

```http
POST   /api/quotes/               # Add quote for a package (admin only)
GET    /api/quotes/?package_id=   # Get all quotes for a package
PUT    /api/quotes/{quote_id}/select  # Customer selects quote
```

---

### 📄 **Invoices**

```http
GET    /api/invoices/?user_id=    # List all invoices for user
POST   /api/invoices/             # Create invoice for selected quote
GET    /api/invoices/{invoice_id}/# Get invoice details
POST   /api/invoices/{invoice_id}/pay   # Simulate payment (or link to payment gateway)
```

---

### 📑 **Shipment Docs**

```http
POST   /api/shipments/            # Upload sender Aadhaar, receiver info
GET    /api/shipments/?invoice_id=# Get shipment info for invoice
```

---

### 🚚 **Dispatch & Tracking**

```http
POST   /api/dispatches/           # Record dispatch and carrier tracking (admin only)
GET    /api/dispatches/{id}/      # Get dispatch info and tracking number
```

---

### 💬 **Feedback**

```http
POST   /api/feedback/             # Submit feedback after shipment
GET    /api/feedback/?user_id=    # List all feedbacks by user (or admin view)
```

---

### 🔄 **Optional: Status Updates**

```http
GET    /api/track/{tracking_number}/     # Live tracking info (if integrated)
```

---

### 📁 **Admin Dashboard Endpoints (Optional)**

```http
GET    /api/admin/pickups/               # View all pickup requests
GET    /api/admin/quotes/pending         # Quotes needing attention
GET    /api/admin/invoices/unpaid        # Unpaid invoices
GET    /api/admin/feedbacks              # View all feedback
```

---

### ✅ **Typical Customer Workflow Using API**

1. `/api/register` → `/api/login`
2. `/api/pickups/` (POST) → `/api/packages/` (POST)
3. Admin adds `/api/quotes/` → User selects `/api/quotes/{id}/select`
4. `/api/invoices/` (POST) → `/api/invoices/{id}/pay`
5. `/api/shipments/` (POST)
6. Admin: `/api/dispatches/` → User gets `/api/dispatches/{id}/`
7. `/api/feedback/` (POST)


Here’s a **clean, role-based Operations Team UI design** for the international shipping workflow. It’s tailored for fast decision-making, clear package tracking, quote management, and document verification.

---

## 📋 **Operations Team Dashboard – UI Design**

---

### 🧭 **Top-Level Navigation (Sidebar / Top Bar)**

* 📦 **Pickup Requests**
* 🎁 **Packages**
* 💰 **Quotes**
* 🧾 **Invoices**
* 📑 **Shipments**
* 🚚 **Dispatch**
* 🔍 **Tracking**
* 💬 **Feedback**
* 👥 **Customers**
* 🛠️ **Admin Tools / Settings**

---

### 1️⃣ **Pickup Requests Page**

**Table View**

| Pickup ID | Customer | Request Date | Pickup Address | Status  | Actions                                 |
| --------- | -------- | ------------ | -------------- | ------- | --------------------------------------- |
| #PK123    | Alice K  | 10-Jul-2025  | Fremont, CA    | Pending | \[📦 View Packages] \[🚚 Assign Pickup] |

**Actions:**

* Filter by date, status
* Assign field agent
* Mark as picked up

---

### 2️⃣ **Packages Page**

**Table View**

| Package ID | Pickup ID | Weight | Status | Contents | Actions                    |
| ---------- | --------- | ------ | ------ | -------- | -------------------------- |
| #PKG2001   | #PK123    | 4 kg   | Boxed  | Sweets   | \[📝 Edit] \[💬 Add Quote] |

**Actions:**

* Add internal notes
* Tag fragile/heavy
* Mark as packaged

---

### 3️⃣ **Carrier Quotes Page**

**Quote Dashboard**

| Package ID | Carrier | Est. Days | Price | Status | Actions                          |
| ---------- | ------- | --------- | ----- | ------ | -------------------------------- |
| #PKG2001   | FedEx   | 5         | \$40  | Sent   | \[✅ Mark Selected] \[🗑️ Remove] |

**Actions:**

* Add quote
* Mark quote selected
* Auto-calculate price suggestions

---

### 4️⃣ **Invoices Page**

| Invoice # | Customer | Amount | Status | Issued Date | Actions                       |
| --------- | -------- | ------ | ------ | ----------- | ----------------------------- |
| INV203    | Alice K  | \$48   | Paid   | 10-Jul      | \[📄 View] \[📤 Download PDF] |

**Actions:**

* Resend invoice
* Mark paid manually (offline payment)
* Link to payment gateway record

---

### 5️⃣ **Shipments Page**

**Form / Table View**

| Shipment ID | Invoice | Receiver Name | Aadhaar | Docs Uploaded | Actions                        |
| ----------- | ------- | ------------- | ------- | ------------- | ------------------------------ |
| SH202       | INV203  | Rahul P.      | Yes     | ✅             | \[📁 View Docs] \[🚚 Dispatch] |

**Actions:**

* Upload/verify documents
* Update receiver info
* Approve for dispatch

---

### 6️⃣ **Dispatch Page**

| Dispatch ID | Carrier | Tracking # | Status     | Date   | Actions                          |
| ----------- | ------- | ---------- | ---------- | ------ | -------------------------------- |
| D1001       | FedEx   | 7845XYZ    | In Transit | 11-Jul | \[🔗 Track] \[📩 Share Tracking] |

**Actions:**

* Generate tracking
* Share via email/WhatsApp
* Mark delivered

---

### 7️⃣ **Feedback Page**

| Feedback ID | User    | Rating | Comments       | Submitted | Actions                       |
| ----------- | ------- | ------ | -------------- | --------- | ----------------------------- |
| F202        | Alice K | ⭐⭐⭐⭐⭐  | Great service! | 12-Jul    | \[📄 View Full] \[📝 Respond] |

---

### 💬 **Customer Profile Page**

Includes:

* Contact details
* Shipping history
* Documents (Aadhaar, etc.)
* Feedback summary

---

### 📱 Mobile-Friendly View

* Tabs for quick actions: 📦 Pickups | 🧾 Invoices | 🚚 Dispatch
* Click-to-call and map integration for pickup addresses

---

### 🔐 Roles & Permissions

* **Ops Agent**: View & manage pickups, packages, quotes
* **Finance Staff**: Manage invoices & payments
* **Supervisor/Admin**: Full access + system settings, logs


