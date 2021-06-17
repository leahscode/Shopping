from store_view import StoreView
import tkinter
import tkinter.messagebox
import sqlite3 as sl
import datetime


class Shop(StoreView):
    def __init__(self):
        # Get the products, and convert it to a list - to be passed
        # into the Frame.
        products = self.get_all_products()
        self.products = self.format_result(products)

        # The arguments for the first frame, as a tuple:
        top_label = 'Products List'
        bottom_label = 'To get larger quantities,\nclick the button multiple times.'
        button1 = 'Add to cart'
        button2 = None
        items_list = self.products
        self.frame1 = (
            self,
            top_label,
            bottom_label,
            button1,
            button2,
            items_list,
        )

        # The arguments for the second frame, as a tuple:
        top_label = 'Cart'
        bottom_label = None
        button1 = 'Remove selected\n items from cart'
        button2 = 'Checkout and Pay'
        items_list = None
        self.frame2 = (
            self,
            top_label,
            bottom_label,
            button1,
            button2,
            items_list,
        )

        # Initialize the Store window, using the above details.
        StoreView.__init__(self, self.frame1, self.frame2)

    # These are overriding the empty methods in the parent class.  "order"
    # refers to whether it's the first or second frame.
    def action1(self, order):
        if order == 1:
            self.add_to_cart()
        elif order == 2:
            self.remove_from_cart()

    def action2(self, order):
        if order == 2:
            self.checkout()

    def get_all_products(self):
        # This method creates and returns the product list from the database.
        # It is called in the __init__ method, to be used in frame1.
        try:
            # Connect to the database
            con = sl.connect('products.db')
            cur = con.cursor()

            # Retrieve all the products
            cur.execute('''SELECT * FROM products''')
            products = cur.fetchall()
            products.sort()

            # Commit the changes to the database and close the connection.
            con.commit()
            con.close()
        except Exception as err:
            print(err)
            return []  # To avoid further errors
        else:
            # Return the list
            return products

    def add_to_cart(self):
        # Retrieve all selected items. Add it to the shopping_cart
        # variable and to the cart listbox (in frame2). The cart list box
        # will be cleared and refilled at every update.
        for i in self.frame1.listbox.curselection():
            self.shopping_cart.append(self.frame1.listbox.get(i))

        # Clear the box from previous items
        self.frame2.listbox.delete(0, 'end')
        # Add the updated list
        for i in range(len(self.shopping_cart)):
            self.frame2.listbox.insert(i, self.shopping_cart[i])

    def remove_from_cart(self):
        # Remove the selected items from the cart variable and list box.
        for i in self.frame2.listbox.curselection()[::-1]:
            del self.shopping_cart[i]
            self.frame2.listbox.delete(i)

    def checkout(self):
        # Check if the shopping_cart is not empty.
        if not self.shopping_cart:
            tkinter.messagebox.showerror(
                '',
                'Cannot check out an empty cart.',
                parent=self.main_frame
                )
        else:
            # Get the date, which identifies the transaction.
            current_date = datetime.datetime.now()
            # The query for inserting the sales info will be passed in to
            # the parent class's checkout method.
            query = '''INSERT INTO sales (items, total, sales_date)
            VALUES (?, ?, ?)'''
            StoreView.checkout(self, current_date, query)

            # Clear the cart listbox and the shopping_cart.
            self.frame2.listbox.delete(0, 'end')
            self.shopping_cart = []

    def show_receipt(self, total, date):
        """ This is called from within StoreView.checkout() """
        # A pop-up message box will display the "receipt", including all
        # the items purchased, the total, and the date and time.
        date_str = date.strftime('%a, %m/%d/%y %I:%M %p')
        msg = [
            'Thank you for shopping at Best Supermarket!!!',
            'Here is your receipt:',
            '',  # empty line
            date_str,
            '']
        # The shopping cart list is joined into a single string, with
        # newline as a separator.  Another empty line is added before
        # showing the total.
        msg.append('\n'.join(self.shopping_cart))
        msg.append('')
        msg.append('Total:  $' + '{:,.2f}'.format(total))
        tkinter.messagebox.showinfo(
            'Receipt for ' + date_str,
            "\n".join(msg),
            parent=self.main_frame
            )


if __name__ == '__main__':
    pass
