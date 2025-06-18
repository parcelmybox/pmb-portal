# ParcelMyBox API Documentation

This document provides information about the ParcelMyBox REST API.

## Base URL

All API endpoints are prefixed with `/api/`.

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. To authenticate:

1. Obtain a token by sending a POST request to `/api/token/` with your username and password:
   ```json
   {
     "username": "your_username",
     "password": "your_password"
   }
   ```

2. Include the token in the `Authorization` header for subsequent requests:
   ```
   Authorization: Bearer <your_token>
   ```

## Available Endpoints

### Authentication
- `POST /api/token/` - Obtain JWT token
- `POST /api/token/refresh/` - Refresh JWT token
- `POST /api/token/verify/` - Verify JWT token

### Users
- `GET /api/users/` - List all users (admin only)
- `GET /api/users/<username>/` - Get user details
- `PUT /api/users/<username>/` - Update user
- `PATCH /api/users/<username>/` - Partially update user
- `DELETE /api/users/<username>/` - Delete user (admin only)

### Addresses
- `GET /api/addresses/` - List user's addresses
- `POST /api/addresses/` - Create new address
- `GET /api/addresses/<id>/` - Get address details
- `PUT /api/addresses/<id>/` - Update address
- `PATCH /api/addresses/<id>/` - Partially update address
- `DELETE /api/addresses/<id>/` - Delete address

### Shipments
- `GET /api/shipments/` - List user's shipments
- `POST /api/shipments/` - Create new shipment
- `GET /api/shipments/<id>/` - Get shipment details
- `PUT /api/shipments/<id>/` - Update shipment
- `PATCH /api/shipments/<id>/` - Partially update shipment
- `DELETE /api/shipments/<id>/` - Delete shipment
- `POST /api/shipments/<id>/generate_bill/` - Generate bill for shipment
- `POST /api/shipments/<id>/generate_invoice/` - Generate invoice for shipment

### Bills
- `GET /api/bills/` - List user's bills
- `POST /api/bills/` - Create new bill
- `GET /api/bills/<id>/` - Get bill details
- `PUT /api/bills/<id>/` - Update bill
- `PATCH /api/bills/<id>/` - Partially update bill
- `DELETE /api/bills/<id>/` - Delete bill

### Invoices
- `GET /api/invoices/` - List user's invoices
- `POST /api/invoices/` - Create new invoice
- `GET /api/invoices/<id>/` - Get invoice details
- `PUT /api/invoices/<id>/` - Update invoice
- `PATCH /api/invoices/<id>/` - Partially update invoice
- `DELETE /api/invoices/<id>/` - Delete invoice

## Filtering and Searching

Most list endpoints support filtering, searching, and ordering:

- `?field=value` - Filter by field value
- `?search=term` - Search across multiple fields
- `?ordering=field` - Order by field (prefix with - for descending)

Example:
```
GET /api/shipments/?status=shipped&ordering=-created_at
```

## Pagination

All list endpoints are paginated. The response includes pagination metadata:

```json
{
  "links": {
    "next": "http://example.com/api/endpoint/?page=2",
    "previous": null
  },
  "count": 100,
  "total_pages": 5,
  "current_page": 1,
  "results": [
    // results...
  ]
}
```

## Error Handling

Errors are returned in the following format:

```json
{
  "detail": "Error message",
  "code": "error_code",
  "status_code": 400
}
```

Common status codes:
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error
