DROP DATABASE IF EXISTS eshop;
CREATE DATABASE IF NOT EXISTS eshop;

USE eshop;

-- create table sales
DROP TABLE IF EXISTS sales;
CREATE TABLE sales (
	sales_id   INT AUTO_INCREMENT PRIMARY KEY,
	sales_name VARCHAR(32) NOT NULL,
	UNIQUE KEY uq_sales_name (sales_name)
);

-- table product
DROP TABLE IF EXISTS products;
CREATE TABLE products (
	product_id   INT AUTO_INCREMENT PRIMARY KEY,
	name_of_item VARCHAR(100) NOT NULL,
	type_of_item ENUM('Phone','Laptop','Accessories') NOT NULL,
	UNIQUE KEY uq_product_name (name_of_item)
);

-- table transaction
DROP TABLE IF EXISTS transactions;
CREATE TABLE transactions (
	txn_id    BIGINT AUTO_INCREMENT,
	sales_id  INT NOT NULL,
	product_id INT NOT NULL,
	units     INT NOT NULL,
	FOREIGN KEY (sales_id) REFERENCES sales (sales_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products (product_id) ON DELETE CASCADE,
    PRIMARY KEY (txn_id,sales_id,product_id)
);

-- summary sales
CREATE OR REPLACE VIEW totalSales AS
SELECT
	s.sales_id             AS salesID,
	s.sales_name           AS salesName,
	p.name_of_item         AS itemName,
	p.type_of_item         AS itemType,
	SUM(t.units)           AS totalUnitSell
FROM transactions t
JOIN sales s    ON s.sales_id   = t.sales_id
JOIN products p ON p.product_id = t.product_id
GROUP BY s.sales_id, s.sales_name, p.name_of_item, p.type_of_item;

-- contoh data
INSERT INTO sales (sales_name) VALUES ('Dewi'), ('Rudi'), ('Sinta'), ('Bayu'), ('Ariq');

INSERT INTO products (name_of_item, type_of_item) VALUES
	('iPhone','Phone'),
	('Zenfone','Phone'),
	('Redminote','Phone'),
	('MacBook','Laptop'),
    ('ROG','Laptop'),
    ('Redmibook','Laptop'),
	('Wireless Mouse','Accessories'),
    ('Airpod','Accessories'),
    ('Mech Keyboard','Accessories');

-- dummy transactions
INSERT INTO transactions (sales_id, product_id, units) VALUES
(1, 1, 6),  
(2, 1, 7),  
(3, 1, 3),
(4, 2, 2),
(5, 2, 3),
(1, 2, 6),
(2, 3, 4),
(3, 3, 2),
(4, 3, 9),
(5, 4, 5),
(1, 4, 4),
(2, 5, 2),
(3, 5, 4),
(4, 6, 2),
(5, 7, 12),
(1, 8, 15),
(2, 9, 17),
(2, 3, 5);  


SELECT * FROM transactions;