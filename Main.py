import tkinter
import sqlite3 as sl
import create_db
import Shop
import Returns
import Sales


class MainScreen:
    # The main screen for the program. If the database is ok, it Will call
    # the "StoreOptions" to display the widgets.  If not, the "NoStore" will
    # give the option to recreate the database.
    def __init__(self):
        self.main_window = tkinter.Tk(className=' Best Supermarket')
        self.main_window.geometry("500x175")

        # Check for the database and see if all tables are ok.
        self.db = self.check_db()
        if self.db[0]:
            # If the first element returned is True, set up the "store" window.
            self.main_frame = StoreOptions(self)
        else:
            # Database not found, show error window.
            self.main_frame = NoStore(self)
        tkinter.mainloop()

    def check_db(self):
        # This method checks if the database tables are set up properly.
        try:
            # Connect to the database
            con = sl.connect('products.db')
            cur = con.cursor()

            # Check if the products table exists
            cur.execute(''' SELECT count(name) FROM sqlite_master
            WHERE type='table' AND name='products' ''')
            products_exists = cur.fetchone()[0]
            if products_exists == 1:
                # Check if the products table is populated - must have at least
                # one item in stock
                cur.execute('''SELECT COUNT(*) FROM products''')
                products_populated = cur.fetchone()[0]
            else:
                # If the table doesn't exist, it is not populated. Required for
                # the return statement, which will be used as an argument for
                # fixing the errors.
                products_populated = 0
            # Check if the sales table exists
            cur.execute(''' SELECT count(name) FROM sqlite_master
                WHERE type='table' AND name='sales' ''')
            sales_exists = cur.fetchone()[0]

            # Commit the changes to the database and close the connection.
            con.commit()
            con.close()
        except Exception as err:
            print(err)
            return (False,)  # To avoid further errors
        else:
            # Return the results
            if products_exists == 0 \
                    or products_populated == 0 \
                    or sales_exists == 0:
                return (False, products_exists, products_populated, sales_exists)
            else:
                return (True,)

    def create_new_store(self):
        # If "Create Database" is selected from the error window:
        # Create the database, and if successful, and display the store.
        if create_db.create_db(self.db):
            # The following refers to the main_frame property from the
            # "NoStore" class, with "NoStore" being the main_frame for
            # this window.
            self.main_frame.main_frame.destroy()
            self.main_frame = StoreOptions(self)
        else:
            # If the database was not successfully created:
            self.main_window.destroy()


class NoStore:
    def __init__(self, upper):

        # If the database is not present or incomplete, the program will
        # display an error message and an option to recreate it.
        self.main_frame = tkinter.Frame(upper.main_window)

        # The message/label:
        txt = 'Welcome to "Best Supermarket"\n'
        txt += 'We are presently unable to locate the database.\n'
        txt += 'But no worries, we can create a new one for you!'
        tkinter.Label(
            self.main_frame,
            text=txt
        ).pack(pady=18, padx=15)

        # "Create" button:
        tkinter.Button(
            self.main_frame,
            text='Create Database',
            width=20,
            command=upper.create_new_store
        ).pack(pady=(0, 15))

        # "Exit" button:
        tkinter.Button(
            self.main_frame,
            text='Exit',
            width=9,
            command=upper.main_window.destroy
        ).pack()

        self.main_frame.pack()


class StoreOptions:
    def __init__(self, upper):
        # Will display a welcome message, and buttons 4 for the store
        # options. Each button's method call is to create a new class/window.
        # Except for the "exit" button, which closes the program.  The Return
        # button uses lambda to enable an error message on the parent frame.
        self.upper = upper
        self.main_frame = tkinter.Frame(upper.main_window)

        # text area:
        tkinter.Label(
            self.main_frame,
            text='Welcome to "Best Supermarket"'
        ).pack(pady=20, padx=15)

        # Buttons:
        self.new_button('Shop', Shop.Shop)
        self.new_button('Return Item', lambda: Returns.Returns(self))
        self.new_button('Sales', Sales.Sales)
        self.new_button('Exit', self.exit)

        self.main_frame.pack()

    def new_button(self, text, cmd):
        # Since we need a lot of buttons with the same style, a function
        # makes sense.
        tkinter.Button(
            self.main_frame,
            text=text,
            width=9,
            command=cmd
        ).pack(side='left', pady=20, padx=15)

    # Method for the exit button:
    def exit(self):
        msg = 'Are you sure that you want to quit?\n You will lose all' \
            ' unsaved data and your shopping cart will be emptied.'
        if tkinter.messagebox.askyesno(message=msg):
            self.upper.main_window.destroy()


if __name__ == '__main__':
    my_store = MainScreen()
