# Courier Business Transaction Module (Inflow/Outflow Focus)

This document outlines the **transaction management system** , specifically focused on **inflow and outflow transactions**. The goal is to maintain a robust and traceable financial backend with multi-currency support and ensures every rupee/dollar is accounted for — across customers, partners, governments, and internal ops

---

##  Objective

To create a scalable backend schema to:
- Record all revenue-generating inflows (payments, subscriptions, add-ons, etc.)
- Capture all outflows (courier bills, operational costs, refunds, etc.)
- Track FX conversions across INR, USD, etc.
- Allow future financial analytics (P&L, cost-per-shipment, etc.)

---

##  Inflow Modules (Revenue Sources)

### 1. **Customer**

**Purpose:** Stores core customer information. Customers initiate and pay for shipments, making this table essential to link transactions and services.

```sql
CREATE TABLE Customer (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(255),
  email VARCHAR(255),
  phone VARCHAR(20)
);
```

### 2. **Shipment**

**Purpose:** Represents each delivery order. Each shipment connects customer details with both revenue (payments) and cost (logistics partners).

```sql
CREATE TABLE Shipment (
  id INT PRIMARY KEY AUTO_INCREMENT,
  customer_id INT,
  origin VARCHAR(255),
  destination VARCHAR(255),
  courier_partner VARCHAR(255),
  status VARCHAR(100),
  created_at DATETIME,
  FOREIGN KEY (customer_id) REFERENCES Customer(id)
);
```

### 3. **Payment**

**Purpose:** Tracks how much the customer paid for a shipment. Includes payment gateway and currency info for multi-national use.

```sql
CREATE TABLE Payment (
  id INT PRIMARY KEY AUTO_INCREMENT,
  shipment_id INT,
  amount_paid DECIMAL(10, 2),
  currency VARCHAR(10),
  gateway VARCHAR(100),
  fee_charged DECIMAL(10, 2),
  paid_at DATETIME,
  FOREIGN KEY (shipment_id) REFERENCES Shipment(id)
);
```

### 4. **AddOnService**

**Purpose:** Captures optional services like insurance or express delivery that generate additional revenue per shipment.

```sql
CREATE TABLE AddOnService (
  id INT PRIMARY KEY AUTO_INCREMENT,
  shipment_id INT,
  name VARCHAR(100),
  price DECIMAL(10, 2),
  currency VARCHAR(10),
  FOREIGN KEY (shipment_id) REFERENCES Shipment(id)
);
```

### 5. **Subscription**

**Purpose:** Used for recurring revenue from customers who subscribe to courier plans (typically businesses).

```sql
CREATE TABLE Subscription (
  id INT PRIMARY KEY AUTO_INCREMENT,
  customer_id INT,
  plan_name VARCHAR(100),
  monthly_fee DECIMAL(10, 2),
  currency VARCHAR(10),
  start_date DATE,
  end_date DATE,
  FOREIGN KEY (customer_id) REFERENCES Customer(id)
);
```

### 6. **ClaimReimbursement**

**Purpose:** When courier partners reimburse the company for delivery delays or damage, this inflow is recorded here.

```sql
CREATE TABLE ClaimReimbursement (
  id INT PRIMARY KEY AUTO_INCREMENT,
  shipment_id INT,
  amount_received DECIMAL(10, 2),
  currency VARCHAR(10),
  received_date DATE,
  notes TEXT,
  FOREIGN KEY (shipment_id) REFERENCES Shipment(id)
);
```

### 7. **WalletTransaction**

**Purpose:** Tracks wallet top-ups by customers and credits issued (e.g., for refunds). Important for prepaid use-cases.

```sql
CREATE TABLE WalletTransaction (
  id INT PRIMARY KEY AUTO_INCREMENT,
  customer_id INT,
  transaction_type ENUM('TopUp', 'Credit', 'Adjustment'),
  amount DECIMAL(10, 2),
  currency VARCHAR(10),
  transaction_time DATETIME,
  reference_note TEXT,
  FOREIGN KEY (customer_id) REFERENCES Customer(id)
);
```

---

##  Outflow Modules (Cost Tracking)

### 1. **CourierCost**

**Purpose:** Logs the amount paid by the business to courier partners. May differ from customer payment due to internal pricing or discounts.

```sql
CREATE TABLE CourierCost (
  id INT PRIMARY KEY AUTO_INCREMENT,
  shipment_id INT,
  courier_name VARCHAR(100),
  amount_billed DECIMAL(10, 2),
  currency VARCHAR(10),
  fx_rate_used DECIMAL(10, 4),
  FOREIGN KEY (shipment_id) REFERENCES Shipment(id)
);
```

### 2. **Refund**

**Purpose:** When the company compensates customers (e.g., delays, damage), this expense is logged here.

```sql
CREATE TABLE Refund (
  id INT PRIMARY KEY AUTO_INCREMENT,
  shipment_id INT,
  reason TEXT,
  amount_refunded DECIMAL(10, 2),
  currency VARCHAR(10),
  refunded_on DATE,
  FOREIGN KEY (shipment_id) REFERENCES Shipment(id)
);
```

### 3. **CustomsFee**

**Purpose:** Records charges paid at borders. Important for international courier tracking and determining whether sender or receiver bears the cost.

```sql
CREATE TABLE CustomsFee (
  id INT PRIMARY KEY AUTO_INCREMENT,
  shipment_id INT,
  amount_paid DECIMAL(10, 2),
  currency VARCHAR(10),
  paid_by ENUM('Sender', 'Receiver'),
  FOREIGN KEY (shipment_id) REFERENCES Shipment(id)
);
```

### 4. **OperationalExpense**

**Purpose:** Captures business expenses like tech, salaries, office rent, SMS APIs. Helps in overall profitability analysis.

```sql
CREATE TABLE OperationalExpense (
  id INT PRIMARY KEY AUTO_INCREMENT,
  description TEXT,
  amount DECIMAL(10, 2),
  currency VARCHAR(10),
  expense_date DATE,
  category VARCHAR(100)
);
```

### 5. **TaxPayment**

**Purpose:** Tracks statutory obligations like GST, TDS, and other tax outflows.

```sql
CREATE TABLE TaxPayment (
  id INT PRIMARY KEY AUTO_INCREMENT,
  tax_type VARCHAR(100),
  amount DECIMAL(10, 2),
  currency VARCHAR(10),
  payment_date DATE,
  notes TEXT
);
```

---

##  FXTransaction (Foreign Exchange Management)

**Purpose:** Handles conversions between INR, USD, etc. Used to normalize multi-currency inflows/outflows for reporting and accounting.

```sql
CREATE TABLE FXTransaction (
  id INT PRIMARY KEY AUTO_INCREMENT,
  related_model VARCHAR(100),
  related_id INT,
  from_currency VARCHAR(10),
  to_currency VARCHAR(10),
  fx_rate DECIMAL(10, 4),
  converted_amount DECIMAL(10, 2),
  transaction_time DATETIME,
  notes TEXT
);
```

---

##  Use Cases

| Use Case                                 | Inflow/Outflow | Currency | Linked Table                   |
| ---------------------------------------- | -------------- | -------- | ------------------------------ |
| Customer pays for US to India courier    | Inflow         | USD      | Payment                        |
| DHL charges backend courier fee          | Outflow        | USD      | CourierCost                    |
| User adds insurance and express option   | Inflow         | INR      | AddOnService                   |
| Business user subscribes to monthly plan | Inflow         | INR      | Subscription                   |
| System reimburses delayed parcel         | Outflow        | INR      | Refund                         |
| Company pays server & tax                | Outflow        | INR      | OperationalExpense, TaxPayment |
| INR/USD conversions on both ends         | Neutral        | FX Rate  | FXTransaction                  |
| Customer tops up wallet for future use   | Inflow         | INR/USD  | WalletTransaction              |


---

> This document ensures every rupee/dollar is accounted for — across customers, partners, governments, and internal ops.



```


