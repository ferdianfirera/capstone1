import pandas as pd
import seaborn as sns
import sys
import mysql.connector
from mysql.connector import Error
import matplotlib.pyplot as plt
from tabulate import tabulate

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "admin123",
    "database": "eshop",
}

def get_conn():
    return mysql.connector.connect(**DB_CONFIG)

def list_sales():
    query = "SELECT sales_id, sales_name FROM sales ORDER BY sales_id;"
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()
        headers = [desc[0] for desc in cur.description]
    
    print("\n List Sales: ")
    if not rows:
        print("(none)")
    else:
        print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))
    return pd.DataFrame(rows, columns=headers)

def list_products():
    query = "SELECT product_id, name_of_item, type_of_item FROM products ORDER BY product_id;"
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()
        headers = [desc[0] for desc in cur.description]

    print("\n List Products : ")
    if not rows:
        print("(none)")
    else:
        print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))
    return pd.DataFrame(rows, columns=headers)

def total_sold_by_sales():
    query = """
        SELECT salesName, SUM(totalUnitSell) AS total_units_sold
        FROM totalSales
        GROUP BY salesName
        ORDER BY total_units_sold DESC;
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()
        headers = [desc[0] for desc in cur.description]
    
    print("\n Total Units Sold by Sales: ")
    if not rows:
        print("(no sales data)")
    else:
        print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))

    return pd.DataFrame(rows, columns=headers)

def total_sold_by_itemType():
    query = """
        SELECT itemType, SUM(totalUnitSell) AS total_units_sold
        FROM totalSales
        GROUP BY itemType
        ORDER BY total_units_sold DESC;
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()
        headers = [desc[0] for desc in cur.description]
        
    print("\n Total Units Sold by Item Type: ")
    if not rows:
        print("(no sales data)")
    else:
        print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))
    
    return pd.DataFrame(rows, columns=headers)

def view_sales_summary():
    query = """
        SELECT salesID, salesName, itemName, itemType, totalUnitSell
        FROM totalSales
        ORDER BY salesID, itemName;
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()
        headers = [desc[0] for desc in cur.description]

    print("\n Sales Summary: \n")
    if not rows:
        print("(no sales yet)")
    else:
        print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))
    
    df = pd.DataFrame(rows, columns=headers)
    
    # sales per item per salesperson
    if not df.empty:
        plt.figure(figsize=(8, 5))
        sns.barplot(data=df, x="salesName", y="totalUnitSell", hue="itemType")
        plt.title("Sales by Salesperson & Item Type")
        plt.ylabel("Total Units Sold")
        plt.xlabel("Salesperson")
        plt.legend(title="Item Type")
        plt.tight_layout()
        plt.show()
    return df


    query = """
        SELECT salesName, itemName, itemType, totalUnitSell
        FROM totalSales
        ORDER BY salesName, itemName;
    """
    try:
        with get_conn() as conn:
            df = pd.read_sql(query, conn)
    except Error as e:
        print(f"Error fetching sales summary: {e}")
        return pd.DataFrame()

    if df.empty:
        print("\n-- Sales Summary (Pivot Table) --")
        print("(no sales yet)")
        return df

    # Reshape the DataFrame to show each salesperson on a single row
    # with columns for each itemType.
    pivot_df = df.pivot_table(
        index='salesName', 
        columns='itemType', 
        values='totalUnitSell', 
        aggfunc='sum'
    ).fillna(0) # Fill NaN values with 0 for a cleaner look

    print("\n-- Sales Summary (Pivot Table) --")
    print(pivot_df)

    # You can also use tabulate for a more formatted text output
    # import tabulate
    # print(tabulate(pivot_df, headers='keys', tablefmt="fancy_grid"))

    # The original plotting code can also be updated to use this new pivot table
    if not pivot_df.empty:
        pivot_df.plot(kind='bar', figsize=(8, 5))
        plt.title("Sales by Salesperson & Item Type (from Pivot Table)")
        plt.ylabel("Total Units Sold")
        plt.xlabel("Salesperson")
        plt.legend(title="Item Type")
        plt.tight_layout()
        plt.show()

    return pivot_df

def recap_sale():
    print("\nPick salesperson and product (use IDs).")
    list_sales()
    list_products()
    try:
        sales_id = int(input("sales_id: ").strip())
        product_id = int(input("product_id: ").strip())
        units = int(input("units sold: ").strip())
        if units <= 0:
            print("Units must be > 0.")
            return
    except ValueError:
        print("Invalid input.")
        return
    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(
                "INSERT INTO transactions (sales_id, product_id, units) VALUES (%s, %s, %s);",
                (sales_id, product_id, units),
            )
            conn.commit()
            print("Sale recorded.")
    except Error as e:
        print("Error:", e)

def add_salesperson():
    name = input("Enter sales name: ").strip()
    if not name:
        print("Name cannot be empty.")
        return
    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("INSERT INTO sales (sales_name) VALUES (%s);", (name,))
            conn.commit()
            print("Salesperson added.")
    except Error as e:
        print("Error:", e)

def avg_sold_by_sales():
    query = """
        SELECT salesName, AVG(totalUnitSell) AS avg_units_sold
        FROM totalSales
        GROUP BY salesName
        ORDER BY avg_units_sold DESC;
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()
        headers = [desc[0] for desc in cur.description]
    
    print("\n Average Units Sold by Salesperson: ")
    if not rows:
        print("(no sales data)")
    else:
        print(tabulate(rows, headers=headers, tablefmt="fancy_grid", floatfmt=".2f"))

    return pd.DataFrame(rows, columns=headers)

def menu_view_data():
    print(
        """
1) Data Product
2) Data Sales
0) Back
""")
    
def menu_add_data():
    print(
        """
1) Add Sales Person
2) Recap a Sale
0) Back 
""")
    
def menu_summary():
    print(
        """
1) Total Sold by Item Type
2) Total Sold by Sales
3) Average Sold by Sales
4) Graphic of Sales Summary
0) Back
""")    

def menu():
    print("""
Electronic Shop Sales App
1) View Data
2) Add Data
3) Summary
0) Exit
""")

def main():
    while True:
        menu()
        choice = input("Choose: ").strip()
        
        try:
            choice = int(choice)
            if choice == 1:
                while True:
                    menu_view_data()
                    sub_choice = input("Choose: ").strip()
                    if sub_choice == "1":
                        list_products()
                    elif sub_choice == "2":
                        list_sales()
                    elif sub_choice == "0":
                        break
                    else:
                        print("Invalid input. Please enter a number from the menu.")
            elif choice == 2:
                while True:
                    menu_add_data()
                    sub_choice = input("Choose: ").strip()
                    if sub_choice == "1":
                        add_salesperson()
                    elif sub_choice == "2":
                        recap_sale()
                    elif sub_choice == "0":
                        break
                    else:
                        print("Invalid input. Please enter a number from the menu.")
            elif choice == 3:
                while True:
                    menu_summary()
                    sub_choice = input("Choose: ").strip()
                    if sub_choice == "1":
                        total_sold_by_itemType()
                    elif sub_choice == "2":
                        total_sold_by_sales()
                    elif sub_choice == "3":
                        avg_sold_by_sales()
                    elif sub_choice == "4":
                        view_sales_summary()
                    elif sub_choice == "0":
                        break
                    else:
                        print("Invalid input. Please enter a number from the menu.")
            elif choice == 0:
                print("Thank you!")
                sys.exit(0)
            else:
                print("Invalid input. Please enter a number from the menu.")
        except ValueError:
            print("Invalid input. Please enter a number from the menu.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()