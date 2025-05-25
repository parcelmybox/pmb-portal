# 📦 ParcelMyBox Shipment Workflow

This document outlines the end-to-end workflow for handling a customer shipment request using the **ParcelMyBox** system. It covers each step from pickup request to delivery confirmation and customer feedback collection.

---

## ✅ Workflow Steps

### 1. Receive Pickup Request
- Request received from the customer (via call, form submission, or email).
- Logged into the **Leads Manager** module.

### 2. Collect Documents from Customer Location
- Executive visits the customer address.
- Documents required for shipment are collected.

### 3. Collect Shipping Inputs (Online/Offline)
- Inputs collected and stored in the **Quote Manager** or **Shipment Handler** module:
  - **Sender**: Name, Address, Phone
  - **Receiver**: Name, Address, Phone
  - **KYC Documents**: PAN, Aadhar, Passport, etc.

### 4. Collect Payment
- Payment collected through:
  - Cash, UPI, Credit/Debit, or Online Gateway
- Transaction recorded in the **Invoice & Payments** module.

### 5. Validate KYC
- Check document validity using internal or external KYC validation tools.
- Required before proceeding with packaging.

### 6. Prepare Package
- Package is packed securely with required protection.
- Dimensions and weight added to the shipment record.

### 7. Generate FedEx Shipping Label
- FedEx API integration triggered from **Rate Manager** or **Partner Selector**.
- Label generated using validated shipping data.

### 8. Affix Label to Package
- Label printed and physically attached to the package.

### 9. Share Tracking Number with Customer
- Tracking number sent via SMS/Email from the **Tracking Module**.

### 10. Add Tracking Number to Watchlist
- Tracking number added to daily monitoring list.
- Delivery status updated regularly in the **Tracking Module**.

### 11. Send Feedback Request
- Once delivery is confirmed:
  - Customer receives a feedback form or message via WhatsApp, Email, or SMS.

---

## 🗺️ Mermaid Flow Diagram

```mermaid
flowchart TD
    A[Receive Pickup Request] --> B[Collect Documents from Customer Location]
    B --> C[Collect Shipping Inputs\n(Sender, Receiver, KYC)]
    C --> D[Collect Payment]
    D --> E[Validate KYC]
    E --> F[Prepare Package]
    F --> G[Generate FedEx Label]
    G --> H[Affix Label to Package]
    H --> I[Share Tracking Number with Customer]
    I --> J[Add Tracking Number to Watchlist\n(Daily Until Delivered)]
    J --> K[Send Feedback Request to Customer\n(After Delivery)]
