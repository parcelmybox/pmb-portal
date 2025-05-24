CREATE TABLE Customers (
    id UUID PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(50),
    billing_address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Enquiries (
    id UUID PRIMARY KEY,
    customer_id UUID REFERENCES Customers(id),
    origin_country VARCHAR(100),
    destination_country VARCHAR(100),
    weight_kg DECIMAL(10, 2),
    document_type VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Carriers (
    id UUID PRIMARY KEY,
    name VARCHAR(100),
    code VARCHAR(50),
    api_url TEXT
);

CREATE TABLE CarrierRates (
    id UUID PRIMARY KEY,
    carrier_id UUID REFERENCES Carriers(id),
    origin_country VARCHAR(100),
    destination_country VARCHAR(100),
    base_rate DECIMAL(10, 2),
    estimated_days INTEGER,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Shipments (
    id UUID PRIMARY KEY,
    customer_id UUID REFERENCES Customers(id),
    carrier_id UUID REFERENCES Carriers(id),
    enquiry_id UUID REFERENCES Enquiries(id),
    tracking_number VARCHAR(100),
    status VARCHAR(50) CHECK (status IN ('pending', 'shipped', 'delivered', 'failed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE ShipmentStatus (
    id UUID PRIMARY KEY,
    shipment_id UUID REFERENCES Shipments(id),
    status VARCHAR(100),
    description TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Payments (
    id UUID PRIMARY KEY,
    shipment_id UUID REFERENCES Shipments(id),
    amount DECIMAL(10, 2),
    payment_method VARCHAR(50),
    payment_status VARCHAR(50),
    transaction_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Documents (
    id UUID PRIMARY KEY,
    shipment_id UUID REFERENCES Shipments(id),
    file_path TEXT,
    file_type VARCHAR(50),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
