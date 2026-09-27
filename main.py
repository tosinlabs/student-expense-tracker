import json 
import os
from datetime import date, timedelta


def calculate_total(expenses):
    total = 0
    
    for item in expenses:
        total += item['amount']
        
    return total


def load_expenses():
    if os.path.exists('expenses.json'):
        with open('expenses.json','r') as file:
            return json.load(file)   
        
    return []


def load_budget():
    if os.path.exists('budget.json'):
        with open('budget.json', 'r') as file:
            return json.load(file)
    
    return {
        "daily": 0.0,
        "weekly": 0.0,
        "monthly": 0.0
    }
    

def save_expenses(expenses):
    with open("expenses.json", "w") as file:
        json.dump(expenses, file, indent=4)

def save_budget(budget):
    with open("budget.json", "w") as file:
        json.dump(budget, file, indent=4)

def show_menu():
    print("======= Student Expense Tracker =======")
    print("1. Add Expense")
    print("2. View Expenses")  
    print("3. Set Budget")  
    print("4. View Budget")  
    print('5. Delete Expense')
    print('6. Edit Expense')
    print("7. Exit")  
    
    choice = input('\nChoose an option: ')
    
    return choice

def add_expense(expenses):
    print('\n==== Add Expense ====')

    while True:
        while True:
            expense = (input('What did you spend money on? ')).strip()
            if not expense:
                print('Expense field cannot be empty!\n')
                continue

            if not expense.replace(" ", "").isalpha():
                print('Expense name can only contain letters!\n')
                continue
                
            break

        while True:
            try:
                amount = float(input('How much did you spend: ₦'))
                if amount <= 0:
                    print('Amount must be greater than ₦0\n')
                    continue
                break
            except ValueError:
                print('Please enter a valid number\n')

        while True:
            category = input('What category is the expense? ').strip()
            
            if not category:
                print('Category field cannot be empty!\n')
                continue
            break
        
        add_item = input('\nWould you like to add another expense? (yes/no): ')
        
        expense_date = str(date.today())
        
        expense_data = {
        'expense': expense,
        'amount': amount,
        'category': category,
        'date':expense_date
    }

        expenses.append(expense_data)
        
        
        if add_item.lower() == 'yes':
            continue
        else: 
            save_expenses(expenses)
            print('\n')
            break
    
 
def view_expenses(expenses): 
    
    total = calculate_total(expenses)
    
    if not expenses:
        print('\nThere are no expenses yet\nAdd an expense to view it.\n')
        return   
    print('\nYour expense(s): ')
    for index, item in enumerate(expenses, start = 1):
        print(f"- Item: {item['expense']}\n- Amount(₦): ₦{item['amount']}\n- Category: {item['category']}\n- Date: {item['date']}\n")
    print(f'\n===== Total Amount Spent: ₦{total:.2f} =====\n')
    
def set_budget(budget):
    print('\n===== Set Budget =====') 
    while True:
        try:
            daily = float(input("Set your daily budget limit: ₦"))
            if daily <= 0:
                print('Daily budget must be greater than ₦0\n')
                continue
                        
            weekly = float(input("Set your weekly budget limit: ₦"))
            if weekly <= 0:
                print('Weekly budget must be greater than than ₦0\n')
                continue
                
            monthly = float(input('Set your monthly budget limit: ₦'))
            if monthly <= 0:
                print('Monthly budget must be greater than ₦0\n')
                continue
    
            break
        except ValueError:
            print('Please enter valid numbers only')
    
    budget['daily'] = daily
    budget['weekly'] = weekly
    budget['monthly'] = monthly
    
    save_budget(budget)

    print('\nBudget Saved Successfully\n')
    
    
def calculate_period_spending(expenses):
    today = date.today()

    daily_spent = 0
    weekly_spent = 0
    monthly_spent = 0

    week_start = today - timedelta(days=today.weekday())

    for item in expenses:
        expense_date = date.fromisoformat(item["date"])

        if expense_date == today:
            daily_spent += item["amount"]

        if week_start <= expense_date <= today:
            weekly_spent += item["amount"]

        if (expense_date.year == today.year and
                expense_date.month == today.month):
            monthly_spent += item["amount"]

    return daily_spent, weekly_spent, monthly_spent



def view_budget(budget, expenses):
    print('\n==== Viewing Budget ====')
    print(f"Daily Budget: ₦{budget['daily']:.2f}")
    print(f"Weekly Budget: ₦{budget['weekly']:.2f}")
    print(f"Monthly Budget: ₦{budget['monthly']:.2f}")
    
    daily_spent, weekly_spent, monthly_spent = calculate_period_spending(expenses)
     
    print(f"\nToday's Spending: ₦{daily_spent:.2f}")
    print(f"This Week's Spending: ₦{weekly_spent:.2f}")
    print(f"This Month's Spending: ₦{monthly_spent:.2f}")

    total_spent = calculate_total(expenses)

    print(f"\n===== Total Spent: ₦{total_spent:.2f} =====\n")
    
    daily_remaining =  budget['daily'] - daily_spent
    weekly_remaining =  budget['weekly'] - weekly_spent
    monthly_remaining =  budget['monthly'] - monthly_spent
    
    print(f'Daily Remaining: ₦{daily_remaining:.2f}')
    print(f'Weekly Remaining: ₦{weekly_remaining:.2f}')
    print(f'Monthly Remaining: ₦{monthly_remaining:.2f}\n')


def delete_expense(expenses):
    if not expenses:
        print('\nThere are no expenses to delete')
        return
    print('\n==== Delete Expense ====')
    for index, item in enumerate(expenses, start=1):
        print(f"{index}. {item['expense']} - ₦{item['amount']:.2f}")

    while True:
        try:
            choice = int(input("\nEnter the expense number to delete: "))

            if choice < 1 or choice > len(expenses):
                print("Please choose a valid expense number.")
                continue

            break

        except ValueError:
            print("Please enter a valid number.")

    selected_expense = expenses[choice - 1]

    confirm_delete = input(f"Are you sure you want to delete "
                           f"'{selected_expense['expense']}'? (yes/no): ")
    
    if confirm_delete.lower() != 'yes':
        print('\nDeletion Cancelled\n')
        return

    delete_expense = expenses.pop(choice - 1)

    save_expenses(expenses)

    print(f"\n'{delete_expense['expense']}' was deleted successfully.\n")
 
 
def edit_expense(expenses):
    if not expenses:
        print('\nThere are no expenses to edit')
        return
    
    print('\n==== Edit Expense ====')
    for index, item in enumerate(expenses, start=1):
        print(f"{index}. {item['expense']} - ₦{item['amount']:.2f}")

    while True:
        try:
            choice = int(input("\nEnter the expense number to edit: "))

            if choice < 1 or choice > len(expenses):
                print("Please choose a valid expense number.")
                continue

            break

        except ValueError:
            print("Please enter a valid number.")

    item = expenses[choice - 1]

    print(f"\nEditing: {item['expense']}")

    while True:
        new_expense = input("Enter new expense name: ").strip()
        if not new_expense:
            print('New Expense field cannot be empty!\n')
            continue
            
        if new_expense.isdigit():
            print('No digit(s) is allowed!\n')
            continue
        
        if not new_expense.replace(' ','').isalpha():
            print('New Expense name can only contain letters!\n')
            continue
        
        break 
    item["expense"] = new_expense
    
    while True:
        try:
            new_amount = float(input("Enter new amount: ₦"))
            if new_amount <= 0:
                print('Amount cannot be negative/less than ₦0\n')
                continue
            break
        except ValueError:
            print('\nEnter a valid number\n')
            
    item['amount'] = new_amount
    
    while True:
        new_category = input("Enter new category: ").strip()

        if not new_category:
            print("New Category field cannot be empty!")
            continue

        break
    
    item['category'] = new_category
    
    save_expenses(expenses)

    print("\nExpense updated successfully!\n")
    


def main():
    
    expenses = load_expenses()
    
    budget = load_budget()
    
    while True:
        choice = show_menu()
    
        if choice == '1':
            add_expense(expenses)
            
        elif choice == "2":
            view_expenses(expenses)

        elif choice == "3":
            set_budget(budget)

        elif choice == "4":
            view_budget(budget, expenses)
        
        elif choice == '5':
            delete_expense(expenses)
            
        elif choice == '6':
            edit_expense(expenses)

        elif choice == "7":
            print("\nGoodbye!")
            break

        else:
            print("\nInvalid option. Please choose 1-7.\n")
main()