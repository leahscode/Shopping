import tkinter
import tkinter.messagebox
import sqlite3 as sl


class StoreView:
    # This base class is used as a template for the "Shop" and "Returns"
    # classes.  Both classes inherit this, with some added methods.
    def __init__(
        self,
        frame1,
        frame2
    ):
        # This window will contain three frames: two StoreFrame objects,
        # and another one at the bottom for the exit button.  The arguments
        # for the StoreFrame objects are tuples, hence the spread operator.

        self.main_frame = tkinter.Toplevel()

        self.end_frame = tkinter.Frame(self.main_frame)
        tkinter.Button(
            self.end_frame,
            text='Exit',
            width=12,
            command=self.quit
        ).pack(pady=15)
        self.end_frame.pack(side='bottom')

        self.frame1 = StoreFrame(1, *frame1)
        self.frame2 = StoreFrame(2, *frame2)

        # Initialize the shopping_cart, which will be used for all shopping
        # and returning actions.
        self.shopping_cart = []

    # These will be overwritten in the inherited class
    def action1(self, order):
        pass

    def action2(self, order):
        pass

    def format_result(self, result):
        # "result" refers to the products returned from an SQL query.  It
        # needs to be converted to a format usable for this program.
        items_list = []
        for item in result:
            item = '{0:04d}   {1}   ${2:,.2f}'.format(
                item[0],
                item[1],
                item[2]
            )
            items_list.append(item)
        return items_list

    def quit(self):
        # Confirm before closing; called when pressing the exit button.
        msg = 'Are you sure that you want to quit?'\
            '\n You will lose all unsaved data.'
        if tkinter.messagebox.askyesno(message=msg, parent=self.main_frame):
            self.main_frame.destroy()

    def checkout(self, date, query):
        try:
            # Connect to the database
            con = sl.connect('products.db')
            cur = con.cursor()

            bar_codes = self.get_barcodes()
            total = self.get_total(cur, bar_codes)
            # Insert the sales data into the sales table.  The items are
            # inserted as a string of barcodes; no need to rewrite the
            # product information, as it can be found in the products table.
            # This would be unacceptable in a real-life shopping app, since
            # prices change.  But it's just fine here; it simplifies the
            # database design.
            cur.execute(query,  ('\t'.join(bar_codes), total, date))

            # Commit the changes to the database and close the connection.
            con.commit()
            con.close()
        except Exception as err:
            print(err)
        else:
            # Display the receipt
            self.show_receipt(total, date)

    """ Helpers for "checkout()" """
    def get_barcodes(self):
        # gets the barcodes of the shopping cart, to be used for the database.
        barcodes = []
        for item in self.shopping_cart:
            barcodes.append(item[:item.find(' ')])
        return barcodes

    def get_total(self, cur, items_list):
        # This is called from within "checkout()".  "items_list" refers to
        # a list of barcodes for all the items in the shopping_cart.
        """
        Must be called from within a method that connects to, and
        disconnects from, the database!!!
        """
        # Retrieve the prices for all the products purchased.  Must use a loop
        # and multiple queries, to accommodate the quantity purchased.
        items = []
        for item in items_list:
            cur.execute('''SELECT price FROM products WHERE barcode =
                (?)''', (item,))
            result = cur.fetchone()
            items.append(result[0])
        # Get the total, by adding all prices.
        total = sum(items)
        # Return the total
        return total

    def show_receipt(self, total, date):
        pass


class StoreFrame:
    def __init__(
        self,
        order,
        parent,
        top_label,
        bottom_label,
        button1,
        button2,
        items_list,
        selectmode='multiple'
    ):
        self.parent = parent
        self.main_frame = parent.main_frame

        # Each of the two frames will contain a listbox, a label on top,
        #  one or two buttons on the bottom, and possible another label.
        self.sub_frame = tkinter.Frame(self.main_frame)

        """ # Create product list and a label for the list. A scroll bar is
        # added, to accommodate larger lists. """

        # The top label is a StringVar because for one frame, it will
        # need to be updated while running.
        self.heading = tkinter.StringVar()
        self.heading.set(top_label)
        tkinter.Label(
            self.sub_frame,
            textvariable=self.heading
            ).pack()

        # The bottom label and buttons are coded in reverse order, to counter
        # the 'side' parameter of the listbox scrollbar.
        if button2 is not None:
            # button2 is optional; not all frames have it.
            tkinter.Button(
                self.sub_frame,
                text=button2,
                width=15,
                command=lambda: self.parent.action2(order)
            ).pack(side='bottom', padx=15)

        tkinter.Button(
            self.sub_frame,
            text=button1,
            width=15,
            command=lambda: self.parent.action1(order)
        ).pack(side='bottom', padx=15)

        if bottom_label is not None:
            # bottom_label is optional; not all frames have it.
            tkinter.Label(
                self.sub_frame,
                text=bottom_label
                ).pack(side='bottom')

        # The scrollbar and listbox - the main focus of the frame.
        scroll_bar = tkinter.Scrollbar(self.sub_frame)
        scroll_bar.pack(side='right', fill='y')
        self.listbox = tkinter.Listbox(
            self.sub_frame,
            width=25,
            yscrollcommand=scroll_bar.set,
            selectmode=selectmode
        )

        # Insert the elements into the list box, assuming an items_list is
        # provided.  "frame2" always starts with an empty listbox.
        if items_list is not None:
            self.fill_listbox(items_list)

        # Pack everything
        self.listbox.pack(side='left', pady=20)
        scroll_bar.config(command=self.listbox.yview)
        self.sub_frame.pack(side='left', padx=15, pady=20)

    def fill_listbox(self, items):
        # This is called when creating the object, as well as during runtime.
        for i in range(len(items)):
            self.listbox.insert(i, items[i])


if __name__ == '__main__':
    pass
