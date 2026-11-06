CREATE TABLE plants (
    plant_code TEXT PRIMARY KEY,
    plant_city TEXT NOT NULL,
    capacity_units INTEGER NOT NULL
);

CREATE TABLE distribution_centers (
    dc_code TEXT PRIMARY KEY,
    dc_city TEXT NOT NULL,
    region TEXT NOT NULL
);

CREATE TABLE items (
    item_sku TEXT PRIMARY KEY,
    item_description TEXT NOT NULL,
    product_group TEXT NOT NULL
);

CREATE TABLE shipments (
    shipment_id INTEGER PRIMARY KEY,
    ship_date DATE NOT NULL,
    item_sku TEXT NOT NULL,
    plant_code TEXT NOT NULL,
    dc_code TEXT NOT NULL,
    units INTEGER NOT NULL,
    net_sales NUMERIC(12,2) NOT NULL
);
