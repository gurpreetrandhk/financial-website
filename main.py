import datetime
import json
import os

def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def display_menu():
    """Displays the main menu."""
    print("\nFinancial Tracker Menu:")
    print("1. Add Transaction")
    print("2. View Summary")
    print("3. View Transactions Table")
    print("4. View Charts")  # Added option for charts
    print("5. Save Data")
    print("6. Exit")

def get_valid_date():
    """Gets a valid date from the user."""
    while True:
        date_str = input("Enter date (YYYY-MM-DD): ")
        try:
            return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")

def get_valid_amount():
    """Gets a valid amount from the user."""
    while True:
        amount_str = input("Enter amount: ")
        try:
            amount = float(amount_str)
            if amount >= 0:
                return amount
            else:
                print("Amount must be non-negative.")
        except ValueError:
            print("Invalid amount format. Please enter a number.")

def get_valid_category():
    """Gets a valid category from the user."""
    categories = ['spending', 'consumption', 'saving', 'income', 'other']
    while True:
        category = input(f"Enter category ({', '.join(categories)}): ").lower()
        if category in categories:
            return category
        else:
            print("Invalid category. Please choose from the list.")

def get_valid_type():
    """Gets a valid transaction type from the user."""
    types = ['debit', 'credit']
    while True:
        transaction_type = input(f"Enter type ({', '.join(types)}): ").lower()
        if transaction_type in types:
            return transaction_type
        else:
            print("Invalid type. Please choose debit or credit.")

def add_transaction(transactions):
    """Adds a new transaction to the list."""
    clear_screen()
    print("Add New Transaction")
    date = get_valid_date()
    description = input("Enter description: ")
    category = get_valid_category()
    amount = get_valid_amount()
    transaction_type = get_valid_type()

    transaction = {
        'id': len(transactions) + 1,  # Simple ID assignment
        'date': date.isoformat(),
        'description': description,
        'category': category,
        'amount': amount,
        'type': transaction_type,
    }
    transactions.append(transaction)
    print("Transaction added successfully.")

def calculate_summary(transactions):
    """Calculates and displays the financial summary."""
    total_debit = sum(t['amount'] for t in transactions if t['type'] == 'debit')
    total_credit = sum(t['amount'] for t in transactions if t['type'] == 'credit')
    balance = total_credit - total_debit
    return total_debit, total_credit, balance

def display_summary(transactions):
    """Displays the financial summary."""
    clear_screen()
    print("Financial Summary")
    total_debit, total_credit, balance = calculate_summary(transactions)
    print(f"Total Debit: ${total_debit:.2f}")
    print(f"Total Credit: ${total_credit:.2f}")
    print(f"Balance: ${balance:.2f}")

def display_transactions(transactions):
    """Displays the transactions in a table format."""
    clear_screen()
    print("Transactions Table")
    if not transactions:
        print("No transactions to display.")
        return

    print("-" * 80)
    print(f"{'ID':<4} {'Date':<12} {'Description':<20} {'Category':<12} {'Type':<8} {'Amount':<10}")
    print("-" * 80)
    for t in transactions:
        print(f"{t['id']:<4} {t['date']:<12} {t['description']:<20} {t['category']:<12} {t['type']:<8} ${t['amount']:<10.2f}")
    print("-" * 80)
    print("\nThis table displays your financial transactions, including the date, description, category, type (debit or credit), and amount.")

def get_category_data(transactions):
    """Groups transactions by category for charting."""
    categories = {}
    for t in transactions:
        category = t['category']
        amount = t['amount']
        if category not in categories:
            categories[category] = 0
        categories[category] += amount
    return categories

def get_date_data(transactions):
    """Groups transactions by date for charting."""
    daily_data = {}
    for t in transactions:
        date = t['date']
        amount = t['amount']
        transaction_type = t['type']
        description = t['description']  # Include description

        if date not in daily_data:
            daily_data[date] = {'debit': 0, 'credit': 0, 'balance': 0, 'description': description}  # Store description
        if transaction_type == 'debit':
            daily_data[date]['debit'] += amount
        else:
            daily_data[date]['credit'] += amount

    # Calculate balance
    balance = 0
    for date in sorted(daily_data.keys()):
        balance += daily_data[date]['credit'] - daily_data[date]['debit']
        daily_data[date]['balance'] = balance
    return daily_data

def display_charts(transactions):
    """Displays the charts (simulated in text)."""
    clear_screen()
    print("Financial Charts (Simulated)")  #  basic text-based "charts"

    if not transactions:
        print("No data to display charts.")
        return

    category_data = get_category_data(transactions)
    print("\nCategory Distribution:")
    for category, amount in category_data.items():
        print(f"{category}: ${amount:.2f}")

    date_data = get_date_data(transactions)
    print("\nDaily Trend:")
    for date, data in date_data.items():
        print(f"{date}: Debit=${data['debit']:.2f}, Credit=${data['credit']:.2f}, Balance=${data['balance']:.2f}, Description={data['description']}") #show description

    print("\nNote:  These are simplified text representations of charts.")
    print("       For actual interactive charts, you would need a GUI library")
    print("       like Matplotlib or a web framework.")
    input("Press Enter to return to the main menu...")

def save_data(transactions, filename="financial_data.json"):
    """Saves the transactions to a JSON file."""
    try:
        with open(filename, 'w') as f:
            json.dump(transactions, f, indent=4)
        print(f"Data saved successfully to {filename}")
    except Exception as e:
        print(f"Error saving data: {e}")

def load_data(filename="financial_data.json"):
    """Loads the transactions from a JSON file."""
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                transactions = json.load(f)
                return transactions
        else:
            return []  # Return an empty list if the file doesn't exist
    except Exception as e:
        print(f"Error loading data: {e}")
        return []  # Return an empty list on error to avoid crashing

def main():
    """Main function to run the financial tracker application."""
    transactions = load_data() # Load at start
    while True:
        display_menu()
        choice = input("Enter your choice: ")

        if choice == '1':
            add_transaction(transactions)
        elif choice == '2':
            display_summary(transactions)
        elif choice == '3':
            display_transactions(transactions)
        elif choice == '4':
            display_charts(transactions) #call the display chart
        elif choice == '5':
            save_data(transactions)
        elif choice == '6':
            print("Exiting application.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()

