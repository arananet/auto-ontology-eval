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

INSERT INTO dim_product (sku, product_name, brand, category, list_price) VALUES
('SKU-1001', 'Alpine Spring Still 1L', 'Alpine Spring', 'Water', '1.20'),
('SKU-1002', 'Alpine Spring Sparkling 1L', 'Alpine Spring', 'Water', '1.40'),
('SKU-1003', 'Alpine Spring Lemon Soda 330ml', 'Alpine Spring', 'Soda', '0.90'),
('SKU-1004', 'Nordwind Apple Juice 1L', 'Nordwind', 'Juice', '2.60'),
('SKU-1005', 'Nordwind Orange Juice 1L', 'Nordwind', 'Juice', '2.80'),
('SKU-1006', 'Nordwind Cola 330ml', 'Nordwind', 'Soda', '0.95'),
('SKU-1007', 'Sol Mar Mango Juice 1L', 'Sol Mar', 'Juice', '3.10'),
('SKU-1008', 'Sol Mar Tonic 330ml', 'Sol Mar', 'Soda', '1.05');

INSERT INTO dim_location (location_id, location_name, city, location_kind) VALUES
('1', 'Lyon Works', 'Lyon', 'plant'),
('2', 'Porto Works', 'Porto', 'plant'),
('3', 'Rotterdam Hub', 'Rotterdam', 'dc'),
('4', 'Milan Depot', 'Milan', 'dc');

INSERT INTO fact_sales (sale_id, sale_date, sku, location_id, units, gross_sales, net_sales) VALUES
('1', '2026-03-04', 'SKU-1002', '3', '48', '67.20', '67.20'),
('2', '2026-03-28', 'SKU-1003', '4', '37', '33.30', '33.30'),
('3', '2026-03-24', 'SKU-1004', '4', '52', '135.20', '135.20'),
('4', '2026-03-06', 'SKU-1005', '4', '21', '58.80', '56.00'),
('5', '2026-03-28', 'SKU-1006', '4', '31', '29.45', '29.45'),
('6', '2026-03-16', 'SKU-1007', '3', '14', '43.40', '43.40'),
('7', '2026-03-27', 'SKU-1002', '3', '20', '28.00', '28.00'),
('8', '2026-03-09', 'SKU-1003', '4', '41', '36.90', '32.40'),
('9', '2026-03-23', 'SKU-1004', '4', '60', '156.00', '156.00'),
('10', '2026-03-15', 'SKU-1005', '4', '40', '112.00', '112.00'),
('11', '2026-03-05', 'SKU-1006', '4', '48', '45.60', '45.60'),
('12', '2026-03-01', 'SKU-1007', '3', '25', '77.50', '62.00'),
('13', '2026-03-03', 'SKU-1002', '3', '42', '58.80', '58.80'),
('14', '2026-03-13', 'SKU-1003', '4', '58', '52.20', '52.20'),
('15', '2026-03-18', 'SKU-1004', '3', '38', '98.80', '98.80'),
('16', '2026-03-20', 'SKU-1005', '4', '30', '84.00', '75.60'),
('17', '2026-03-24', 'SKU-1006', '4', '51', '48.45', '48.45'),
('18', '2026-03-03', 'SKU-1007', '3', '14', '43.40', '43.40'),
('19', '2026-03-05', 'SKU-1002', '4', '25', '35.00', '35.00'),
('20', '2026-03-11', 'SKU-1003', '3', '39', '35.10', '33.30'),
('21', '2026-03-27', 'SKU-1004', '4', '12', '31.20', '31.20'),
('22', '2026-03-11', 'SKU-1005', '3', '50', '140.00', '140.00'),
('23', '2026-03-01', 'SKU-1006', '3', '35', '33.25', '33.25'),
('24', '2026-03-24', 'SKU-1007', '4', '37', '114.70', '99.20');

INSERT INTO sales_returns (return_id, sale_id, return_date, return_amount) VALUES
('1', '4', '2026-04-06', '2.80'),
('2', '8', '2026-04-09', '4.50'),
('3', '12', '2026-04-01', '15.50'),
('4', '16', '2026-04-20', '8.40'),
('5', '20', '2026-04-11', '1.80'),
('6', '24', '2026-04-24', '15.50');
