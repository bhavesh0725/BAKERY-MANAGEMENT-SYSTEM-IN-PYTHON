#!/usr/bin/env python
# coding: utf-8

# In[15]:


import datetime
import pytz
import json
import os
import xlsxwriter
from reportlab.pdfgen import canvas

class Order:
    order_counter = 0 #This variable will be used to keep track of the total number of orders.


    def __init__(self, customer_name, items, quantities):
        Order.order_counter += 1 # accessing class variable inside class
        self.order_id = Order.order_counter
        self.customer_name = customer_name
        self.items = items
        self.quantities = quantities
        self.order_date = datetime.datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M:%S") 
        #stores the current date and time in the 'Asia/Kolkata' timezone.

    def display_order_details(self, menu):
        #This method is responsible for displaying detailed information about a specific order,
        #including the order ID, customer name, order date, a breakdown of items with their quantities,
        #individual prices, and total cost. The menu parameter is used to look up the prices of items 
        #from a predefined menu.
        print("\nOrder Details:")
        print("Order ID:", self.order_id)
        print("Customer Name:", self.customer_name)
        print("Order Date:", self.order_date)
        print("\nItems:")
        total_price = 0

        for item, quantity in zip(self.items, self.quantities):
            price = menu[item]
            item_total = price * quantity
            total_price += item_total
            print(f"{item} - Quantity: {quantity} - Price: {price} Rs - Total: {item_total} Rs")

        print("\nTotal Price: Rs ", total_price)

    def to_dict(self):
        #The to_dict method in the Order class is designed to convert an instance of the class into 
        #a dictionary. This can be useful for various purposes, such as saving the order data to a file,
        #transmitting it over a network, or converting it to a format that can be easily manipulated in
        #code.
        return {
            'order_id': self.order_id,
            'customer_name': self.customer_name,
            'items': self.items,
            'quantities': self.quantities,
            'order_date': self.order_date
        }

class BakeryManagementSystem:
    def __init__(self):
        self.orders = []
        self.menu = {
            'Pizza': 85.0,
            'Burger': 50.0,
            'Cake': 200.0,
            'Cookies': 25.0,
            'Croissant': 30.0,
            'Muffin': 40.0
            
        }

    def load_order_history(self):
        #the load_order_history method reads order data from a JSON file and converts it into a list of
        #Order instances, populating the self.orders list with the loaded order information. This 
        #method is useful for initializing the BakeryManagementSystem with historical order data stored
        #in a file
        if os.path.exists('order_history.json'):
            with open('order_history.json', 'r') as file:
                order_data = json.load(file)
                self.orders = [Order(customer_name=order['customer_name'],
                                     items=order['items'],
                                     quantities=order['quantities']) for order in order_data]

    def save_order_history(self):
        #the save_order_history method, the 'order_history.json' file will contain a JSON representation 
        #of the order data, where each order is represented as a dictionary. This file can be later used 
        #to load the order data back into the program using the load_order_history method.
        
        order_data = [order.to_dict() for order in self.orders]
        with open('order_history.json', 'w') as file:
            json.dump(order_data, file, indent=4)


    def export_to_excel(self):
        #Check if there are any orders:
        if not self.orders:
            print("No orders to export.")
            return
        #Create a new Excel workbook and worksheet:
        workbook = xlsxwriter.Workbook('order_history.xlsx')
        worksheet = workbook.add_worksheet()
        
        #Write headers (column) to the worksheet:
        headers = ['Order ID', 'Customer Name', 'Items', 'Quantities', 'Order Date']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header)
        
        
        #Write order details (rows) to the worksheet:
        for row, order in enumerate(self.orders, start=1):
            worksheet.write(row, 0, order.order_id)
            worksheet.write(row, 1, order.customer_name)
            worksheet.write(row, 2, ', '.join(order.items))
            worksheet.write(row, 3, ', '.join(map(str, order.quantities)))
            worksheet.write(row, 4, order.order_date)

        workbook.close()
        print("Order history exported to Excel successfully!")



    def export_to_pdf(self, order_id):
        for order in self.orders:
            if order.order_id == order_id:
                pdf_filename = f'bill_order_{order_id}.pdf'
                canvas_obj = canvas.Canvas(pdf_filename)

                canvas_obj.drawString(72, 800, "Order Bill")
                canvas_obj.drawString(72, 780, f"Order ID: {order.order_id}")
                canvas_obj.drawString(72, 760, f"Customer Name: {order.customer_name}")
                canvas_obj.drawString(72, 740, f"Order Date: {order.order_date}")

                y_position = 720
                for item, quantity in zip(order.items, order.quantities):
                    price = self.menu[item]
                    item_total = price * quantity
                    canvas_obj.drawString(72, y_position, f"{item} - Quantity: {quantity} - Price: {price} Rs - Total: {item_total} Rs")
                    y_position -= 20

                total_price = sum(self.menu[item] * quantity for item, quantity in zip(order.items, order.quantities))
                canvas_obj.drawString(72, y_position, f"Total Price: {total_price} Rs")

                canvas_obj.save()
                print(f"Bill exported to {pdf_filename}")
                return
        print("Order not found.")

    def add_order(self, customer_name):
        items = []
        quantities = []

        print("\nMenu:")
        for item, price in self.menu.items():
            print(f"{item} - Rs {price}")

        while True:
            item = input("Enter item from the menu (or 'Done' to finish): ")
            if item == 'done' or item =='Done':
                break

            if item in self.menu:
                quantity = int(input(f"Enter quantity for {item}: "))
                items.append(item)
                quantities.append(quantity)
            else:
                print("Invalid item. Please choose from the menu.")

        new_order = Order(customer_name, items, quantities)
        self.orders.append(new_order)
        print("\nOrder added successfully!")
        return new_order.order_id

    def get_order_details(self, order_id):
        for order in self.orders:
            if order.order_id == order_id:
                order.display_order_details(self.menu)
                return
        print("Order not found.")

    def modify_order(self, order_id):
        for order in self.orders:
            if order.order_id == order_id:
                print("\nCurrent Order Details:")
                order.display_order_details(self.menu)

                items = []
                quantities = []

                print("\nMenu:")
                for item, price in self.menu.items():
                    print(f"{item} - ${price}")

                while True:
                    item = input("Enter item from the menu to modify (or 'done' to finish): ")
                    if item.lower() == 'done':
                        break

                    if item in self.menu:
                        quantity = int(input(f"Enter new quantity for {item}: "))
                        items.append(item)
                        quantities.append(quantity)
                    else:
                        print("Invalid item. Please choose from the menu.")

                order.items = items
                order.quantities = quantities
                order.order_date = datetime.datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M:%S")
                print("\nOrder modified successfully!")
                return
        print("Order not found.")

def main():
    bakery_system = BakeryManagementSystem()
    bakery_system.load_order_history()

    while True:
        print("\nBakery Management System")
        print("1. Add Order")
        print("2. Get Order Details")
        print("3. Modify Order")
        print("4. Export Order History to Excel")
        print("5. Export Bill to PDF")
        print("6. Exit")

        choice = input("Enter your choice (1-6): ")

        if choice == "1":
          customer_name = input("Enter Customer Name: ")
          order_id = bakery_system.add_order(customer_name)
          print(f"Order ID: {order_id}")

        elif choice == "2":
          order_id = int(input("Enter Order ID to retrieve details: "))
          bakery_system.get_order_details(order_id)

        elif choice == "3":
          order_id = int(input("Enter Order ID to modify: "))
          bakery_system.modify_order(order_id)

        elif choice == "4":
          bakery_system.export_to_excel()
          print("Order history exported to Excel successfully!")

        elif choice == "5":
          order_id = int(input("Enter Order ID to export bill to PDF: "))
          bakery_system.export_to_pdf(order_id)

        elif choice == "6":
          bakery_system.save_order_history()
          print("Exiting Bakery Management System. Order history saved. Goodbye!")
          break

        else:
          print("Invalid choice. Please enter a number between 1 and 6.")

if __name__ == "__main__":
  main()

