import tkinter
import matplotlib.figure as fg
import matplotlib.backends.backend_tkagg as mbbt
import sqlite3 as sl
import numpy as np
import datetime


# This list mimics a switch-case. The first index is not used.
# Will be used to retrieve the correct month name, based on the number.
MONTH_NAMES = [
    None,
    'January',
    'February',
    'March',
    'April',
    'May',
    'June',
    'July',
    'August',
    'September',
    'October',
    'November',
    'December'
]


class Sales:
    def __init__(self):
        self.main_frame = tkinter.Toplevel()
        self.main_frame.geometry("700x400")

        # Create two frames, so it can be displayed side by side.
        self.list_frame = tkinter.Frame(self.main_frame)
        tkinter.Label(
            self.list_frame,
            text="Choose a month, to display sales data."
        ).pack()

        # Create radio buttons, so user can select a month. The graph is
        # displayed automatically when the selection changes.
        self.month_num = tkinter.IntVar()
        for x in range(1, 13):
            tkinter.Radiobutton(
                self.list_frame,
                text=MONTH_NAMES[x],
                variable=self.month_num,
                value=x,
                command=self.show_data
            ).pack(anchor='w', padx=10)
        self.list_frame.pack(side='left', padx=20, pady=20)

        # Create the second frame, for the graph. It will be destroyed
        # and re-created for every graph. This way, the user doesn't
        # need to close any windows before seeing the next graph.
        self.plot_frame = tkinter.Frame(self.main_frame)
        self.plot_frame.pack(side='left', padx=20, pady=20)
        self.show_data()

    def show_data(self):
        # Show the data, with the help of the methods below.
        selected_month = self.month_num.get()
        if selected_month == 0:
            # For first run, when the app loads and nothing is selected,
            # it will display the data for the current month.
            selected_month = datetime.datetime.now().strftime('%m')
        sales_data = self.get_sales_data(selected_month)
        # Verify that sales data is retrieved successfully.  Check if any
        # sales data is present for at least one day of the month, or if
        # it's all zero.  Create the x-coordinates, the title and labels;
        # and display graph.
        title = 'Sales Data for ' + str(MONTH_NAMES[int(selected_month)])
        if self.no_data_added(sales_data):
            title += '\n No sales data recorded for this month.'

        self.plot_frame.destroy()
        self.plot_data(sales_data, title)

    def plot_data(self, sales_data, title):
        # The frame
        self.plot_frame = tkinter.Frame(self.main_frame)
        # The figure that will contain the plot, and the plot itself.
        # It uses the sales_data list generated in the method that calls
        # it. The title represents the month for which the data is.
        self.fig = fg.Figure(figsize=(5, 5), dpi=100)
        ax = self.fig.add_subplot(111)
        # The title and labels
        ax.set_title(title)
        ax.set_xlabel('Day of Month')
        ax.set_ylabel('Sales Total in Dollars')
        # The x-coordinates
        days = np.arange(1, 32)

        ax.bar(days, sales_data)
        canvas = mbbt.FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()
        self.plot_frame.pack(side='left')

    def get_sales_data(self, month):
        # Creates a list of sales data.  List is initialized as "0" per day,
        # and uses "+=" to allow for multiple purchases.
        # The day of the month is matched to the list index.  That element
        # is then updated with the new sales data.
        # The list starts with an extra element, since index
        # numbers start at zero, but month days start at one.  The first
        # index is then removed, since no day is numbered as zero.
        sales_data = [0] * 32
        month = str(month).zfill(2)
        fetched_data = self.fetch_data(month)
        for item in fetched_data:
            day = int(item[0])
            total = float(item[1])
            sales_data[day] += total

        # Remove first element (there is no day #0).
        sales_data.pop(0)
        return sales_data

    def fetch_data(self, month):
        # Retrieve all sales data for a given month.  The day of the month
        # is also retrieved, so that the data can be graphed accordingly.
        # (The year is ignored.)

        # Connect to the database
        try:
            con = sl.connect('products.db')
            cur = con.cursor()
            # Execute the Query
            cur.execute('''SELECT strftime('%d', sales_date), total FROM sales WHERE
                    strftime('%m', sales_date) = (?)''', (month,))
            result = cur.fetchall()
            # Commit the changes to the database and close the connection.
            con.commit()
            con.close()
        except Exception as err:
            print(err)
            return []  # To avoid further errors
        else:
            return result

    def no_data_added(self, list_):
        # Checks if any sales data has been found.  For empty graph,
        # the heading will be adjusted accordingly.
        for x in range(len(list_)):
            if list_[x] != 0:
                return False
        return True
