-- Drop tables safely (order + CASCADE matters)
DROP TABLE IF EXISTS orderdetails CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS payments CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS employees CASCADE;
DROP TABLE IF EXISTS offices CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS productlines CASCADE;

-- Tables
CREATE TABLE productlines (
  "productLine" VARCHAR(50) PRIMARY KEY,
  "textDescription" VARCHAR(4000),
  "htmlDescription" TEXT,
  "image" BYTEA
);

CREATE TABLE products (
  "productCode" VARCHAR(15) PRIMARY KEY,
  "productName" VARCHAR(70) NOT NULL,
  "productLine" VARCHAR(50) NOT NULL,
  "productScale" VARCHAR(10) NOT NULL,
  "productVendor" VARCHAR(50) NOT NULL,
  "productDescription" TEXT NOT NULL,
  "quantityInStock" INTEGER NOT NULL,
  "buyPrice" NUMERIC(10,2) NOT NULL,
  "MSRP" NUMERIC(10,2) NOT NULL,
  FOREIGN KEY ("productLine") REFERENCES productlines("productLine")
);

CREATE TABLE offices (
  "officeCode" VARCHAR(10) PRIMARY KEY,
  "city" VARCHAR(50) NOT NULL,
  "phone" VARCHAR(50) NOT NULL,
  "addressLine1" VARCHAR(50) NOT NULL,
  "addressLine2" VARCHAR(50),
  "state" VARCHAR(50),
  "country" VARCHAR(50) NOT NULL,
  "postalCode" VARCHAR(15) NOT NULL,
  "territory" VARCHAR(10) NOT NULL
);

CREATE TABLE employees (
  "employeeNumber" INTEGER PRIMARY KEY,
  "lastName" VARCHAR(50) NOT NULL,
  "firstName" VARCHAR(50) NOT NULL,
  "extension" VARCHAR(10) NOT NULL,
  "email" VARCHAR(100) NOT NULL,
  "officeCode" VARCHAR(10) NOT NULL,
  "reportsTo" INTEGER,
  "jobTitle" VARCHAR(50) NOT NULL,
  FOREIGN KEY ("reportsTo") REFERENCES employees("employeeNumber"),
  FOREIGN KEY ("officeCode") REFERENCES offices("officeCode")
);

CREATE TABLE customers (
  "customerNumber" INTEGER PRIMARY KEY,
  "customerName" VARCHAR(50) NOT NULL,
  "contactLastName" VARCHAR(50) NOT NULL,
  "contactFirstName" VARCHAR(50) NOT NULL,
  "phone" VARCHAR(50) NOT NULL,
  "addressLine1" VARCHAR(50) NOT NULL,
  "addressLine2" VARCHAR(50),
  "city" VARCHAR(50) NOT NULL,
  "state" VARCHAR(50),
  "postalCode" VARCHAR(15),
  "country" VARCHAR(50) NOT NULL,
  "salesRepEmployeeNumber" INTEGER,
  "creditLimit" NUMERIC(10,2),
  FOREIGN KEY ("salesRepEmployeeNumber") REFERENCES employees("employeeNumber")
);

CREATE TABLE payments (
  "customerNumber" INTEGER,
  "checkNumber" VARCHAR(50),
  "paymentDate" DATE NOT NULL,
  "amount" NUMERIC(10,2) NOT NULL,
  PRIMARY KEY ("customerNumber", "checkNumber"),
  FOREIGN KEY ("customerNumber") REFERENCES customers("customerNumber")
);

CREATE TABLE orders (
  "orderNumber" INTEGER PRIMARY KEY,
  "orderDate" DATE NOT NULL,
  "requiredDate" DATE NOT NULL,
  "shippedDate" DATE,
  "status" VARCHAR(15) NOT NULL,
  "comments" TEXT,
  "customerNumber" INTEGER NOT NULL,
  FOREIGN KEY ("customerNumber") REFERENCES customers("customerNumber")
);

CREATE TABLE orderdetails (
  "orderNumber" INTEGER,
  "productCode" VARCHAR(15),
  "quantityOrdered" INTEGER NOT NULL,
  "priceEach" NUMERIC(10,2) NOT NULL,
  "orderLineNumber" SMALLINT NOT NULL,
  PRIMARY KEY ("orderNumber", "productCode"),
  FOREIGN KEY ("orderNumber") REFERENCES orders("orderNumber"),
  FOREIGN KEY ("productCode") REFERENCES products("productCode")
);

-- Sample data for testing
INSERT INTO productlines ("productLine", "textDescription") VALUES
  ('Classic Cars', 'Detailed die-cast and plastic model cars'),
  ('Motorcycles', 'Real motorcycles and scale motorcycle models'),
  ('Planes', 'Complete collection of die-cast airplane and helicopter models'),
  ('Ships', 'Model ships and boats'),
  ('Trains', 'Model trains and railroad sets'),
  ('Trucks and Buses', 'Model trucks and buses');

INSERT INTO products VALUES
  ('S10_1678', '1969 Harley Davidson Ultimate Chopper', 'Motorcycles', '1:10', 'Min Lin Diecast', 'This replica features working kickstand, front forks, and steering. All parts are particularly delicate due to their precise scale and require special care and attention.', 7933, 48.81, 95.70),
  ('S10_1949', '1952 Alpine Renault 1300', 'Classic Cars', '1:10', 'Classic Metal Creations', 'Turnable front wheels; steering function; detailed interior with seat adjuster; right hand drive', 7305, 98.30, 214.30),
  ('S10_2016', '1996 Moto Guzzi 1100i', 'Motorcycles', '1:10', 'Highway 66 Mini Classics', 'Official Moto Guzzi logos and insignias, saddle bags with stuff and removable, this is a reproduction of the original 1996 Moto Guzzi 1100i', 6625, 68.99, 118.94),
  ('S12_1099', '1968 Ford F-150', 'Trucks and Buses', '1:12', 'Motor City Art Classics', 'The operating parts of this power-up, electric and other vehicles will exceed the useful life of the APIs in fact. It has a fifty-fifty chance to be the next toy to be stored in the closet.', 8693, 45.25, 99.35);

INSERT INTO offices VALUES
  ('1', 'San Francisco', '+1 650 219 4782', '100 Market Street', NULL, 'CA', 'USA', '94080', 'NA'),
  ('2', 'Boston', '+1 215 837 0597', '1550 Court Place', 'Suite 102', 'MA', 'USA', '02107', 'NA'),
  ('3', 'NYC', '+1 212 555 3000', '445 Park Avenue', NULL, 'NY', 'USA', '10022', 'NA'),
  ('4', 'Paris', '+33 1 42 34 39 46', '43 Rue Jouffroy D''Abbans', NULL, NULL, 'France', '75017', 'EMEA'),
  ('5', 'Tokyo', '+81 33 224 5000', '4-1 Kioicho', NULL, 'Chiyoda', 'Japan', '102-8578', 'Japan'),
  ('6', 'Sydney', '+61 2 9264 2451', '5-11 Wentworth Avenue', 'Floor #2', 'NSW', 'Australia', '2010', 'APAC');

INSERT INTO employees VALUES
  (1002, 'Murphy', 'Diane', 'x5800', 'dmurphy@classicmodelcars.com', '1', NULL, 'President'),
  (1056, 'Taylor', 'Leslie', 'x4611', 'ltaylor@classicmodelcars.com', '1', 1002, 'VP Sales'),
  (1076, 'Firrelli', 'Jeff', 'x9273', 'jfirrelli@classicmodelcars.com', '1', 1002, 'VP Marketing'),
  (1088, 'Patterson', 'William', 'x4871', 'wpatterson@classicmodelcars.com', '2', 1056, 'Sales Manager'),
  (1102, 'Bondur', 'Gerhard', 'x5408', 'gbondur@classicmodelcars.com', '4', 1056, 'Sales Manager'),
  (1143, 'Bow', 'Anthony', 'x5428', 'abow@classicmodelcars.com', '1', 1056, 'Sales Manager');

INSERT INTO customers VALUES
  (103, 'Atelier graphique', 'Schmitt', 'Carine', '40.32.2555', '54 rue Royale', NULL, 'Nantes', NULL, '44000', 'France', 1370, 21000.00),
  (112, 'Signal Gift Stores', 'King', 'Jean', '7025551838', '2560 Apollo Road', NULL, 'Las Vegas', 'NV', '89109', 'USA', 1166, 71800.00),
  (114, 'Australian Collectors, Co.', 'Ferguson', 'Peter', '03 9520 4555', '636 St Kilda Road', 'Level 3', 'Melbourne', 'Victoria', '3004', 'Australia', 1611, 117000.00),
  (119, 'La Rochelle Gifts', 'Labrune', 'Janine', '40.67.8555', '67 rue des Cinquante Otages', NULL, 'Nantes', NULL, '44000', 'France', 1370, 118200.00),
  (121, 'Baane Mini Imports', 'Bergulfsen', 'Jonas', '07-98 9555', 'Erling Skakkes gate 78', NULL, 'Stavern', NULL, '4110', 'Norway', 1504, 81700.00);

INSERT INTO orders VALUES
  (10100, '2003-01-06', '2003-01-13', '2003-01-10', 'Shipped', NULL, 103),
  (10101, '2003-01-09', '2003-01-18', '2003-01-11', 'Shipped', NULL, 112),
  (10102, '2003-01-10', '2003-01-18', '2003-01-14', 'Shipped', 'Check on availability', 114),
  (10103, '2003-01-29', '2003-02-07', '2003-02-12', 'Shipped', NULL, 119),
  (10104, '2003-01-31', '2003-02-09', '2003-02-12', 'Shipped', NULL, 121);

INSERT INTO orderdetails VALUES
  (10100, 'S10_1678', 30, 95.70, 1),
  (10100, 'S12_1099', 50, 99.35, 2),
  (10101, 'S10_1949', 22, 214.30, 1),
  (10102, 'S10_2016', 45, 118.94, 1),
  (10103, 'S10_1678', 35, 95.70, 1),
  (10104, 'S12_1099', 28, 99.35, 1);

INSERT INTO payments VALUES
  (103, 'JM555205', '2003-02-10', 14571.44),
  (112, 'OM314933', '2003-01-18', 5249.95),
  (114, 'GG31455', '2003-02-13', 25833.14),
  (119, 'NG94694', '2003-02-15', 8284.84),
  (121, 'DB046203', '2003-02-16', 27042.83);
