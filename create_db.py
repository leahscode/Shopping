import sqlite3 as sl


products = [
    ('0001', 'kiddush wine', '9.99'),
    ('0010', 'bread', '3.50'),
    ('0011', 'candles', '2.00'),
    ('0201', 'apples', '9.99'),
    ('0210', 'orange', '3.50'),
    ('0211', 'grapes', '2.00'),
    ('3001', 'tomato', '9.99'),
    ('3010', 'potato', '3.50'),
    ('3011', 'ketchup', '2.00'),
    ('4001', 'cooking wine', '9.99'),
    ('4010', 'cookies', '3.50'),
    ('4011', 'bottled water', '2.00'),
    ('5001', 'kiddush cup', '9.99'),
    ('5010', 'whole wheat bread', '3.50'),
    ('5011', 'scented candles', '2.00'),
    ('6001', 'orange juice', '9.99'),
    ('6010', 'milk', '3.50'),
    ('6011', 'pudding', '2.00'),
    ('9001', 'yogurt', '9.99'),
    ('9010', 'bagels', '3.50'),
    ('9011', 'tissues', '2.00')
]


def create_db(param):
    # This method sets up the database, if necessary.

    try:
        # Connect to the database
        con = sl.connect('products.db')
        cur = con.cursor()

        # param is a the tuple returned from check_db(). The first one, a
        # boolean, is not used here. For the other values, if it's zero, the
        # required queries will be executed.
        if param[1] == 0:
            # Create the products table.
            cur.execute('''CREATE TABLE products (
                barcode MEDIUMINT NOT NULL PRIMARY KEY,
                product_name VARCHAR(20),
                price REAL
                );''')
        if param[2] == 0:
            # Populate the table with the "inventory" list.
            cur.executemany('''INSERT INTO products(barcode, product_name, price)
                VALUES (?, ?, ?)''', products)
        if param[3] == 0:
            # Create the sales table.
            cur.execute('''CREATE TABLE sales (
                sales_date TIMESTAMP,
                items TEXT,
                total REAL
                );''')

        # Commit the changes to the database and close the connection.
        con.commit()
        con.close()
    except Exception as err:
        print(err)
        # return for verification.
        return False
    else:
        return True  # success
