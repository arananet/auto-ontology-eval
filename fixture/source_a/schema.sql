CREATE TABLE dim_product (
    sku TEXT PRIMARY KEY,
    product_name TEXT NOT NULL,
    brand TEXT NOT NULL,
    category TEXT NOT NULL,
    list_price NUMERIC(12,2) NOT NULL
);

CREATE TABLE dim_location (
    location_id INTEGER PRIMARY KEY,
    location_name TEXT NOT NULL,
    city TEXT NOT NULL,
    location_kind TEXT NOT NULL
);

CREATE TABLE fact_sales (
    sale_id INTEGER PRIMARY KEY,
    sale_date DATE NOT NULL,
    sku TEXT NOT NULL,
    location_id INTEGER NOT NULL,
    units INTEGER NOT NULL,
    gross_sales NUMERIC(12,2) NOT NULL,
    net_sales NUMERIC(12,2) NOT NULL
);

CREATE TABLE sales_returns (
    return_id INTEGER PRIMARY KEY,
    sale_id INTEGER NOT NULL,
    return_date DATE NOT NULL,
    return_amount NUMERIC(12,2) NOT NULL
);
