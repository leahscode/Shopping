from store_view import StoreView
import tkinter
import tkinter.messagebox
import sqlite3 as sl


class Returns(StoreView):
    def __init__(self, parent):
        # Get the products, and convert it to a list - to be passed
        # into the Frame.
        self.sales_dates = self.get_sales_dates()
        if len(self.sales_dates) == 0:
            tkinter.messagebox.showerror(
                '',
                'No previous orders found.',
                parent=parent.main_frame
                )
        else:

            # The arguments for the first frame, as a tuple:
            top_label = 'Select a receipt to view it'
            bottom_label = None
            button1 = 'View Receipt'
            button2 = 'Refresh List'
            items_list = self.format_dates(self.sales_dates)
            self.frame1 = (
                self,
                top_label,
                bottom_label,
                button1,
                button2,
                items_list,
                'single'
            )

            # The arguments for the second frame, as a tuple:
            top_label = ''
            bottom_label = None
            button1 = 'Return selected items'
            button2 = 'End Review'
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
            self.view_receipt()
        elif order == 2:
            self.return_items()

    def action2(self, order):
        if order == 1:
            self.refresh()
        elif order == 2:
            self.end_review()

    def get_sales_dates(self):
        # This method creates and returns the sales dates from the database.
        # It is called in the __init__ method, to be used in frame1.
        try:
            # Connect to the database
            con = sl.connect(
                'products.db',
                detect_types=sl.PARSE_DECLTYPES | sl.PARSE_COLNAMES)
            cur = con.cursor()

            cur.execute('''SELECT sales_date FROM sales''')
            result = cur.fetchall()
            con.commit()
            con.close()
        except Exception as err:
            print(err)
            return []  # To avoid further errors
        else:
            sales_list = []
            for item in result:
                sales_list.append(item[0])
            return sales_list

        """  """
    def format_dates(self, date_list):
        # Will return a list of formatted dates, to be inserted in the
        # listbox.  It will maintain a parallel relationship with the original
        # list, which will still be used for the database - since the database
        # requires datetime objects, not string.
        new_list = []
        for item in date_list:
            new_list.append(item.strftime('%a, %m/%d/%y %I:%M %p'))
        return new_list

    def view_receipt(self):
        if not self.frame1.listbox.curselection():
            # Make sure a receipt is selected.
            tkinter.messagebox.showerror(
                message='Please select a receipt to view it.',
                parent=self.main_frame
            )
        elif self.frame2.listbox.size() > 0:
            # Make sure another receipt isn't open.
            msg = 'You cannot view more than one receipt at a time.\n' \
                'Do you want to close the open receipt?\n' \
                'You will lose all unsaved data.'
            if tkinter.messagebox.askyesno(message=msg, parent=self.main_frame):
                self.clear_receipt_frame()
                self.update_receipt_frame()

        else:
            # Retrieve the receipt
            self.update_receipt_frame()
            """  """

    def update_receipt_frame(self):
        # Retrieve the receipt's info: the items and the date. Note
        # that "receipt" refers to the filename.
        self.receipt_date = \
            self.sales_dates[self.frame1.listbox.curselection()[0]]
        t = tkinter.StringVar()
        t.set(self.receipt_date)
        self.frame2.heading.set(self.receipt_date.strftime('%a, %m/%d/%y %I:%M %p'))
        """  """
        receipt_info = self.get_receipt_info()
        self.shopping_cart = receipt_info[0]
        self.frame2.fill_listbox(self.shopping_cart)

    def get_receipt_info(self):
        # This method retrieves the sales data for a given receipt date.
        try:
            # Connect to the database
            con = sl.connect('products.db')
            cur = con.cursor()

            # Retrieve the data
            cur.execute('''SELECT items, total FROM sales WHERE
            sales_date = (?)''', (self.receipt_date,))
            result = cur.fetchone()
            # Split the barcodes into a list, and get the product information.
            barcodes = result[0].split('\t')
            items = self.get_items(cur, barcodes)
            total = result[1]

            # Commit the changes to the database and close the connection.
            con.commit()
            con.close()
        except Exception as err:
            print(err)
            return ([], 0)  # To avoid further errors
        else:
            # Return the results
            return (items, total)

    def get_items(self, cur, barcodes):
        # Retrieve the product information for all the barcodes in the list.
        # Must use a loop and multiple queries, to accommodate the quantities.
        items = []
        for item in barcodes:
            cur.execute('''SELECT * FROM products WHERE
                barcode = (?)''', (item,))
            items.append(cur.fetchall()[0])
        # Convert the results to the format needed for this program.
        items = self.format_result(items)
        return items

    def refresh(self):
        self.sales_dates = self.get_sales_dates()
        self.frame1.listbox.delete(0, 'end')
        self.frame1.fill_listbox(self.format_dates(self.sales_dates))

    def return_items(self):
        # Confirm the return, proceed if confirmed.
        if tkinter.messagebox.askyesno(
            message='Are you sure you want to return these items?',
            parent=self.main_frame
        ):
            # Get the selected items (index numbers) and delete from the
            # shopping_cart - which is accessed in checkout().
            for i in self.frame2.listbox.curselection()[::-1]:
                del self.shopping_cart[i]

            if len(self.shopping_cart) == 0:
                self.delete_sale()
            else:
                # The query for updating the sales info will be passed in to
                # the parent class's checkout method.
                query = '''UPDATE sales SET items = (?), total = (?)
                WHERE sales_date = (?)'''
                self.checkout(self.receipt_date, query)

            self.clear_receipt_frame()

    def delete_sale(self):
        try:
            # Connect to the database
            con = sl.connect('products.db')
            cur = con.cursor()

            # Delete this row from the sales table.
            # "LIMIT 1" throws an error, so I omitted this precaution.
            cur.execute('''DELETE FROM sales WHERE sales_date = (?)''',
                        (self.receipt_date,))
            # Commit the changes to the database and close the connection.
            con.commit()
            con.close()
        except Exception as err:
            print(err)
        else:
            # Show a confirmation message
            msg = 'All items for {} were successfully returned'.format(
                self.receipt_date.strftime("%c")
            )
            tkinter.messagebox.showinfo(
                message=msg,
                parent=self.main_frame
                )

            # Update the receipt list to reflect the deletion.
            self.refresh()

    def show_receipt(self, total, date):
        # A pop-up message box will display the "receipt", including all
        # the items purchased, the total, and the date and time. Note
        # that a nearly identical method is also in the Sales class.
        date_str = date.strftime('%a, %m/%d/%y %I:%M %p')
        msg = [
            'Items returned successfully.',
            'Here is your updated receipt:',
            '',  # empty line
            date_str,
            '']
        msg.append('\n'.join(self.shopping_cart))
        msg.append('')
        msg.append('Total:  $' + '{:,.2f}'.format(total))
        tkinter.messagebox.showinfo(
            'Receipt for ' + date_str,
            "\n".join(msg),
            parent=self.main_frame
            )

    def end_review(self):
        # When the user is done viewing a receipt, without returning anything.
        msg = 'Are you sure that you are done?'\
            '\n You will lose all unsaved data.'
        if tkinter.messagebox.askyesno(message=msg, parent=self.main_frame):
            self.clear_receipt_frame()

    def clear_receipt_frame(self):
        # Called after a return, or when hitting the "End Review" button.
        self.frame2.heading.set('')
        self.frame2.listbox.delete(0, 'end')
        self.shopping_cart = []
