CREATE TABLE Vendors (
    VendorID SERIAL PRIMARY KEY,
    VENDOR_NAME VARCHAR(255) NOT NULL,
    VENDOR_ADDRESS TEXT,
    VENDOR_PHONE VARCHAR(50),
    VENDOR_URL VARCHAR(255),
    -- Additional address fields if necessary
    CITY VARCHAR(255),
    STATE VARCHAR(255),
    COUNTRY VARCHAR(255),
    ZIP_CODE VARCHAR(20),
    UNIQUE (VENDOR_NAME, VENDOR_ADDRESS, VENDOR_PHONE)
);