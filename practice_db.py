import sqlite3 as sl
# import datetime


def checkout(date, items_list):
    # This method: to be updated
    print(type(date))

    # Connect to the database
    con = sl.connect('products.db')
    cur = con.cursor()

    items = []

    total = sum(items)
    str = '\t'.join(items_list)

    cur.execute('''INSERT INTO sales (sales_date, items, total)
         VALUES (?, ?, ?)''', (date, str,  total))
    #  VALUES (?, 'foo', ?)''', (date,  total))

    cur.execute('select * from sales where sales_date = (?)', (date,))
    d = cur.fetchone()
    print(d)

    # Commit the changes to the database and close the connection.
    con.commit()
    con.close()

    # Return the total
    return total


def get_item(cur, date):
    # warning: will not work yet
    cur.execute('''SELECT strftime('%d', sales_date), total FROM sales WHERE
             strftime('%m', sales_date) = (?)''', (date,))
    # cur.execute('''select strftime('%m', sales_date)  FROM Sales''')
    d = cur.fetchall()
    print(d)


def main():
    # Connect to the database
    con = sl.connect('products.db')
    cur = con.cursor()

    # cur.execute('''select sales_date from sales''')
    # print(cur.fetchall())
    get_item(cur, '06')

    # Commit the changes to the database and close the connection.
    con.commit()
    con.close()


if __name__ == '__main__':
    main()
    # lis = [1, 2, 3, 4, 5]
    # checkout(datetime.datetime.now, lis)
