# 📦 Django Shipping Estimate Web App

A Django-based web app that calculates shipping estimates based on pickup location, destination, carrier, and package size. Inspired by the "Quote Me" section of [ParcelMyBox](https://parcelmybox.com/).

---

## 🚀 Features

- 📍 Choose pickup city and destination ZIP/country
- 🚚 Select carrier (DHL, FedEx, UPS)
- 📦 Choose package type (Document/Box)
- 📐 Dynamic input for package dimensions (if Box)
- 🔢 Calculates volumetric weight
- 💰 Calculates dynamic shipping price
- ⏱️ Displays estimated shipping days
- 🌐 Simple REST API to access order data
- 🎨 Styled similar to ParcelMyBox

---

## 🧠 Shipping Logic

### Volumetric Weight (for Box)

volumetric_weight = (length × width × height) / 5000

### Price 
price = volumetric_weight × rate_per_kg


- `rate_per_kg` is currently set to ₹3000
- Delivery estimates are randomized between 3–7 days

---


## 📦 API

- **Endpoint:** `/api/orders/`
- **Method:** `GET`
- **Description:** Returns all created shipping orders in JSON format, sorted by newest first.
- **Example Response:**

```json
[
  {
    "id": 1,
    "pickup_city": "Hyderabad",
    "destination_country": "USA",
    "destination_zip": "34765",
    "carrier": "DHL",
    "package_type": "Box",
    "length": 20.0,
    "width": 15.0,
    "height": 10.0,
    "volumetric_weight": 0.6,
    "price": 1800.0,
    "ship_days": 3,
    "created_at": "2025-06-02 10:23:45"
  },
  ...
]
```

---

## 🖼️ Screenshots

### Form Page

![Form Page]( <img width="949" alt="form" src="https://github.com/user-attachments/assets/e523e977-0cfa-4876-8a5f-5a9a78335f11" />

)

### Result Page

![Result Page](result)

### API JSON Response

![API Response](<img width="959" alt="json" src="https://github.com/user-attachments/assets/edab2efc-ea92-4ecd-b922-5185ca3f4807" />
)



