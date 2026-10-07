import tkinter as tk
from datetime import date, timedelta
import json
import os
from tkinter import messagebox
from tkinter import ttk

def confirm_exit():
    answer = messagebox.askyesno(
        "Exit",
        "Do you really want to exit?"
    )

    if answer:
        window.destroy()


def load_budget():
    if os.path.exists("budget.json"):
        try:
            with open("budget.json", "r") as file:
                budget = json.load(file)

            if all(
                key in budget
                for key in ("daily", "weekly", "monthly")
            ):
                return budget

        except (json.JSONDecodeError, TypeError):
            pass

    return {
        "daily": 0.0,
        "weekly": 0.0,
        "monthly": 0.0
    }

def calculate_monthly_spending():
    expenses = load_expenses()

    today = date.today()

    total = 0

    for item in expenses:
        expense_date = date.fromisoformat(item["date"])

        if (
            expense_date.year == today.year
            and expense_date.month == today.month
        ):
            total += item["amount"]

    return total


def calculate_daily_spending():
    expenses = load_expenses()

    today = str(date.today())
    total = 0

    for item in expenses:
        if item["date"] == today:
            total += item["amount"]

    return total

def calculate_weekly_spending():
    expenses = load_expenses()

    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())

    total = 0

    for item in expenses:
        expense_date = date.fromisoformat(item["date"])

        if start_of_week <= expense_date <= today:
            total += item["amount"]

    return total

def load_expenses():
    if os.path.exists("expenses.json"):
        try:
            with open("expenses.json", "r") as file:
                expenses = json.load(file)

            if isinstance(expenses, list):
                return expenses

        except (json.JSONDecodeError, TypeError):
            pass

    return []


def save_expenses(expenses):
    with open('expenses.json', 'w')as file:
        json.dump(expenses, file, indent = 4)    

def set_budget_window():
    global set_budget_window_instance

    if (
        set_budget_window_instance is not None
        and set_budget_window_instance.winfo_exists()
    ):
        set_budget_window_instance.lift()
        set_budget_window_instance.focus()
        return
    
    budget_window = tk.Toplevel(window)
    set_budget_window_instance = budget_window
    
    budget_window.title("Set Budget")
    budget_window.geometry("400x300")
    budget_form = ttk.Frame(budget_window)
    budget_form.pack(pady=30)
    
    daily_label = ttk.Label(
    budget_form,
    text="Daily Budget (₦)"
    )
    daily_label.grid(
        row=0,
        column=0,
        padx=10,
        pady=10,
        sticky="w"
    )

    daily_entry = ttk.Entry(budget_form)
    daily_entry.grid(
        row=0,
        column=1,
        padx=10,    
        pady=10
    )
    
    weekly_label = ttk.Label(
    budget_form,
    text="Weekly Budget (₦)"
    )
    weekly_label.grid(
        row=1,
        column=0,
        padx=10,
        pady=10,
        sticky="w"
    )

    weekly_entry = ttk.Entry(budget_form)
    weekly_entry.grid(
        row=1,
        column=1,
        padx=10,
        pady=10
    )
    
    monthly_label = ttk.Label(
    budget_form,
    text="Monthly Budget (₦)"
    )
    monthly_label.grid(
        row=2,
        column=0,
        padx=10,
        pady=10,
        sticky="w"
    )

    monthly_entry = ttk.Entry(budget_form)
    monthly_entry.grid(
        row=2,
        column=1,
        padx=10,
        pady=10
    )
    
    budget = load_budget()

    daily_entry.insert(0, str(budget["daily"]))
    weekly_entry.insert(0, str(budget["weekly"]))
    monthly_entry.insert(0, str(budget["monthly"]))
    
    
    def save_budget():
        daily = daily_entry.get().strip()
        weekly = weekly_entry.get().strip()
        monthly = monthly_entry.get().strip()

        if not daily or not weekly or not monthly:
            messagebox.showwarning(
            "Missing Budget",
            "Please enter all three budget amounts."
        )
            return

        try:
            daily = float(daily)
            weekly = float(weekly)
            monthly = float(monthly)

        except ValueError:
            messagebox.showwarning(
                "Invalid Budget",
                "Only numbers are allowed."
            )
            return
        
        if daily <= 0 or weekly <= 0 or monthly <= 0:
            messagebox.showwarning(
                "Invalid Budget",
                "All budgets must be greater than ₦0."
            )
            return
    
        if daily > weekly or weekly > monthly:
            messagebox.showwarning(
                "Invalid Budget",
                "Budgets must follow Daily ≤ Weekly ≤ Monthly."
            )
            return

        budget = {
        "daily": daily,
        "weekly": weekly,
        "monthly": monthly
        }

        with open("budget.json", "w") as file:
            json.dump(budget, file, indent=4)
            
        messagebox.showinfo(
            "Budget Saved",
            "Your budget has been saved successfully!"
        )
        
        global set_budget_window_instance
        set_budget_window_instance = None


        budget_window.destroy()
            
    save_button = ttk.Button(
    budget_window,
    text="Save Budget",
    command=save_budget
    )

    save_button.pack(pady=10)
       
    button_frame = ttk.Frame(budget_window)
    button_frame.pack(pady=10)   
       

def view_budget_window():
    
    global budget_window

    if budget_window is not None and budget_window.winfo_exists():
        budget_window.lift()
        budget_window.focus()
        return
    budget = load_budget()
    
    daily_spending = calculate_daily_spending()
    
    daily_remaining = budget["daily"] - daily_spending
    weekly_spending = calculate_weekly_spending()
    weekly_remaining = budget["weekly"] - weekly_spending
    monthly_spending = calculate_monthly_spending()
    monthly_remaining = budget["monthly"] - monthly_spending
    budget_window = tk.Toplevel(window)
    budget_window.title("View Budget")
    budget_window.geometry("400x500")

    title_label = ttk.Label(
        budget_window,
        text="Budget Overview",
        font=("Arial", 18, "bold")
    )
    title_label.pack(pady=(20, 15))

    budget_frame = ttk.Frame(budget_window)
    budget_frame.pack(pady=10)
    
    daily_heading = ttk.Label(
    budget_frame,
    text="Daily",
    font=("Arial", 12, "bold")
    )
    daily_heading.pack(pady=(5, 2))

    daily_label = ttk.Label(
        budget_frame,
        text=f"Daily Budget: ₦{budget['daily']:,.2f}"
    )
    daily_label.pack(pady=5)
    
    daily_spent_label = ttk.Label(
    budget_frame,
    text=f"Daily Spent: ₦{daily_spending:,.2f}"
    )
    daily_spent_label.pack(pady=5)
    
    daily_remaining_label = ttk.Label(
    budget_frame,
    text=f"Daily Remaining: ₦{daily_remaining:,.2f}", font=("Arial", 10, "bold")
    )
    daily_remaining_label.pack(pady=5)
    
    separator = ttk.Separator(
    budget_frame,
    orient="horizontal"
    )
    separator.pack(
        fill="x",
        padx=20,
        pady=(10, 5)
    )
    
    weekly_heading = ttk.Label(
    budget_frame,
    text="Weekly",
    font=("Arial", 12, "bold")
    )
    weekly_heading.pack(pady=(15, 2))

    weekly_label = ttk.Label(
        budget_frame,
        text=f"Weekly Budget: ₦{budget['weekly']:,.2f}"
    )
    weekly_label.pack(pady=5)
    
    weekly_spent_label = ttk.Label(
    budget_frame,
    text=f"Weekly Spent: ₦{weekly_spending:,.2f}"
    )
    weekly_spent_label.pack(pady=5)
    
    weekly_remaining_label = ttk.Label(
    budget_frame,
    text=f"Weekly Remaining: ₦{weekly_remaining:,.2f}", font=("Arial", 10, "bold")
    )
    weekly_remaining_label.pack(pady=5)
    
    separator = ttk.Separator(
    budget_frame,
    orient="horizontal"
    )
    separator.pack(
        fill="x",
        padx=20,
        pady=(10, 5)
    )
    
    monthly_heading = ttk.Label(
    budget_frame,
    text="Monthly",
    font=("Arial", 12, "bold")
    )
    monthly_heading.pack(pady=(15, 2))

    monthly_label = ttk.Label(
        budget_frame,
        text=f"Monthly Budget: ₦{budget['monthly']:,.2f}"
    )
    monthly_label.pack(pady=5)
    
    monthly_spent_label = ttk.Label(
    budget_frame,
    text=f"Monthly Spent: ₦{monthly_spending:,.2f}"
    )
    monthly_spent_label.pack(pady=5)
    
    monthly_remaining_label = ttk.Label(
    budget_frame,
    text=f"Monthly Remaining: ₦{monthly_remaining:,.2f}", font=("Arial", 10, "bold")
    )
    monthly_remaining_label.pack(pady=5)


def add_expense():
    expense = expense_entry.get().strip()
    amount = amount_entry.get().strip()
    category = category_entry.get().strip()
    
    if not expense or not category or category == "--Select A Category--":
        messagebox.showwarning(
            "Missing Information",
            "Kindly fill all required fields above."
        )
        return

    if not expense.replace(' ','').isalpha():
        messagebox.showwarning('Invalid Expense name','Expense name can only contain letters.')
        return
    
    try:
        amount = float(amount)
        if amount <= 0:
            messagebox.showwarning('Invalid Amount','Amount must be greater than ₦0.')
            return
    except ValueError:
        messagebox.showerror('Invalid Amount', "Only numbers are allowed.")
        return

    new_expense = {
        'expense':expense,
        'amount':float(amount),
        'category':category,
        'date':str(date.today())
    }
    
    expenses = load_expenses()

    expenses.append(new_expense)
    save_expenses(expenses)
    
    expense_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)
    category_entry.set("")
    
    messagebox.showinfo(
    "Expense Added",
    "Expense added successfully!"
    )
    

def view_expenses():
    global view_window

    if view_window is not None and view_window.winfo_exists():
        view_window.lift()
        view_window.focus()
        return

    expenses = load_expenses()

    if not expenses:
        messagebox.showinfo(
            "No Expenses",
            "You haven't added any expenses yet."
        )
        return

    expense_window = tk.Toplevel(window)
    view_window = expense_window

    def close_view_window():
        global view_window
        view_window = None
        expense_window.destroy()

    expense_window.protocol(
        "WM_DELETE_WINDOW",
        close_view_window
    )

    expense_window.title("View Expenses")
    expense_window.geometry("500x400")

    total = sum(item["amount"] for item in expenses)

    search_frame = ttk.Frame(expense_window)
    search_frame.pack(pady=(10, 0))

    search_label = ttk.Label(
        search_frame,
        text="Search:"
    )
    search_label.pack(side="left", padx=5)

    search_entry = ttk.Entry(
        search_frame,
        width=25
    )
    search_entry.pack(side="left", padx=5)

    table_frame = ttk.Frame(expense_window)
    table_frame.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=10
    )

    style = ttk.Style()

    style.configure(
        "Treeview.Heading",
        font=("Arial", 11, "bold")
    )

    style.configure(
        "Treeview",
        rowheight=30,
        font=("Arial", 10)
    )

    table = ttk.Treeview(
        table_frame,
        columns=("Expense", "Amount", "Category", "Date"),
        show="headings"
    )

    table.heading("Expense", text="Expense")
    table.heading("Amount", text="Amount")
    table.heading("Category", text="Category")
    table.heading("Date", text="Date")

    table.column(
        "Expense",
        width=150,
        anchor="w"
    )

    table.column(
        "Amount",
        width=100,
        anchor="e"
    )

    table.column(
        "Category",
        width=120,
        anchor="center"
    )

    table.column(
        "Date",
        width=110,
        anchor="center"
    )

    scrollbar = ttk.Scrollbar(
        table_frame,
        orient="vertical",
        command=table.yview
    )

    table.configure(
        yscrollcommand=scrollbar.set
    )

    table.pack(
        side="left",
        fill="both",
        expand=True
    )

    scrollbar.pack(
        side="right",
        fill="y"
    )

    def search_expenses():
        search_text = search_entry.get().strip().lower()
        selected_category = category_filter.get()
        selected_sort = sort_option.get()

        filtered_expenses = []

        for item in expenses:
            matches_search = (
                search_text in item["expense"].lower()
            )

            matches_category = (
                selected_category == "All Categories"
                or item["category"] == selected_category
            )

            if matches_search and matches_category:
                filtered_expenses.append(item)

        if selected_sort == "Amount: Low to High":
            filtered_expenses.sort(
                key=lambda item: item["amount"]
            )

        elif selected_sort == "Amount: High to Low":
            filtered_expenses.sort(
                key=lambda item: item["amount"],
                reverse=True
            )

        elif selected_sort == "Date: Newest First":
            filtered_expenses.sort(
                key=lambda item: item["date"],
                reverse=True
            )

        elif selected_sort == "Date: Oldest First":
            filtered_expenses.sort(
                key=lambda item: item["date"]
            )

        elif selected_sort == "Expense: A to Z":
            filtered_expenses.sort(
                key=lambda item: item["expense"].lower()
            )

        for row in table.get_children():
            table.delete(row)

        for item in filtered_expenses:
            table.insert(
                "",
                "end",
                values=(
                    item["expense"],
                    f"₦{item['amount']:,.2f}",
                    item["category"],
                    item["date"]
                )
            )

        sort_dropdown.bind(
            "<<ComboboxSelected>>",
            lambda event: search_expenses()
        )
    
    search_button = ttk.Button(
        search_frame,
        text="Search",
        command=search_expenses
    )

    search_button.pack(
        side="left",
        padx=5
    )
    
    category_filter = tk.StringVar()
    category_filter.set("All Categories")

    category_dropdown = ttk.Combobox(
        search_frame,
        textvariable=category_filter,
        values=(
            "All Categories",
            "Food",
            "Transport",
            "Gifts",
            "Educational",
            "Utensils",
            "Accessories",
            "Schools",
            "Bills",
            "Shopping",
            "Other"
        ),
        state="readonly",
        width=18
    )

    category_dropdown.pack(
        side="left",
        padx=5
    )
    
    category_dropdown.bind(
        "<<ComboboxSelected>>",
        lambda event: search_expenses()
    )
    
    sort_option = tk.StringVar()
    sort_option.set("Sort By")

    sort_dropdown = ttk.Combobox(
        search_frame,
        textvariable=sort_option,
        values=(
            "Sort By",
            "Amount: Low to High",
            "Amount: High to Low",
            "Date: Newest First",
            "Date: Oldest First",
            "Expense: A to Z"
        ),
        state="readonly",
        width=20
    )

    sort_dropdown.pack(
        side="left",
        padx=5
    )

    for item in expenses:
        table.insert(
            "",
            "end",
            values=(
                item["expense"],
                f"₦{item['amount']:,.2f}",
                item["category"],
                item["date"]
            )
        )

    def select_expense(event):
        selected_item = table.selection()

        if selected_item:
            values = table.item(
                selected_item[0],
                "values"
            )
            print(values)

    table.bind(
        "<<TreeviewSelect>>",
        select_expense
    )

    total_frame = ttk.Frame(expense_window)
    total_frame.pack(
        fill="x",
        padx=10,
        pady=(0, 10)
    )

    total_label = ttk.Label(
        total_frame,
        text=f"Total Amount Spent: ₦{total:,.2f}",
        font=("Arial", 14, "bold")
    )

    total_label.pack(anchor="e")

    def delete_selected():
        selected_item = table.selection()

        if not selected_item:
            messagebox.showwarning(
                "No Expense Selected",
                "Please select an expense to delete."
            )
            return

        values = table.item(
            selected_item[0],
            "values"
        )

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Delete '{values[0]}'?"
        )

        if not confirm:
            return

        expenses.pop(
            table.index(selected_item[0])
        )

        save_expenses(expenses)

        table.delete(selected_item[0])

        new_total = sum(
            item["amount"]
            for item in expenses
        )

        total_label.config(
            text=f"Total Amount Spent: ₦{new_total:,.2f}"
        )

        messagebox.showinfo(
            "Expense Deleted",
            "Expense deleted successfully!"
        )

    delete_button = ttk.Button(
        expense_window,
        text="Delete Selected",
        command=delete_selected
    )

    delete_button.pack(
        pady=(0, 10)
    )

    def edit_selected():
        selected_item = table.selection()

        if not selected_item:
            messagebox.showwarning(
                "No Expense Selected",
                "Please select an expense to edit."
            )
            return

        values = table.item(
            selected_item[0],
            "values"
        )

        edit_window = tk.Toplevel(
            expense_window
        )

        edit_window.title("Edit Expense")
        edit_window.geometry("400x350")

        ttk.Label(
            edit_window,
            text="Expense"
        ).pack(pady=(15, 5))

        edit_expense_entry = ttk.Entry(
            edit_window
        )

        edit_expense_entry.pack()

        edit_expense_entry.insert(
            0,
            values[0]
        )

        ttk.Label(
            edit_window,
            text="Amount"
        ).pack(pady=(10, 5))

        edit_amount_entry = ttk.Entry(
            edit_window
        )

        edit_amount_entry.pack()

        edit_amount_entry.insert(
            0,
            values[1].replace("₦", "").replace(",", "")
        )

        ttk.Label(
            edit_window,
            text="Category"
        ).pack(pady=(10, 5))

        edit_category_entry = tk.StringVar()

        edit_category_entry.set(
            values[2]
        )

        edit_category_dropdown = ttk.Combobox(
            edit_window,
            textvariable=edit_category_entry,
            values=(
                "Food",
                "Transport",
                "Gifts",
                "Educational",
                "Utensils",
                "Accessories",
                "Schools",
                "Bills",
                "Shopping",
                "Other"
            ),
            state="readonly",
            width=20
        )

        edit_category_dropdown.pack()

        def save_changes():
            new_expense = edit_expense_entry.get().strip()
            new_amount = edit_amount_entry.get().strip()
            new_category = edit_category_entry.get().strip()

            if not new_expense:
                messagebox.showwarning(
                    "Invalid Expense",
                    "Expense name cannot be empty."
                )
                return

            if not new_expense.replace(
                " ",
                ""
            ).isalpha():
                messagebox.showwarning(
                    "Invalid Expense",
                    "Expense name can only contain letters."
                )
                return

            try:
                new_amount = float(
                    new_amount
                )

                if new_amount <= 0:
                    messagebox.showwarning(
                        "Invalid Amount",
                        "Amount must be greater than ₦0."
                    )
                    return

            except ValueError:
                messagebox.showwarning(
                    "Invalid Amount",
                    "Only numbers are allowed for the amount."
                )
                return

            if not new_category:
                messagebox.showwarning(
                    "Invalid Category",
                    "Category cannot be empty."
                )
                return

            selected_index = table.index(
                selected_item[0]
            )

            expenses[selected_index]["expense"] = new_expense
            expenses[selected_index]["amount"] = new_amount
            expenses[selected_index]["category"] = new_category

            save_expenses(expenses)

            table.item(
                selected_item[0],
                values=(
                    new_expense,
                    f"₦{new_amount:,.2f}",
                    new_category,
                    expenses[selected_index]["date"]
                )
            )

            new_total = sum(
                item["amount"]
                for item in expenses
            )

            total_label.config(
                text=f"Total Amount Spent: ₦{new_total:,.2f}"
            )

            messagebox.showinfo(
                "Expense Updated",
                "Expense updated successfully!"
            )

            edit_window.destroy()

        button_frame = ttk.Frame(
            edit_window
        )

        button_frame.pack(
            pady=25
        )

        save_button = ttk.Button(
            button_frame,
            text="Save Changes",
            command=save_changes
        )

        save_button.pack(
            side="left",
            padx=5
        )

        discard_button = ttk.Button(
            button_frame,
            text="Discard",
            command=edit_window.destroy
        )

        discard_button.pack(
            side="left",
            padx=5
        )

    edit_button = ttk.Button(
        expense_window,
        text="Edit Selected",
        command=edit_selected
    )

    edit_button.pack(
        pady=(0, 10)
    )


def reports_window():
    expenses = load_expenses()

    report_window = tk.Toplevel(window)
    report_window.title("Reports")
    report_window.geometry("500x600")

    title_label = ttk.Label(
        report_window,
        text="Spending Reports",
        font=("Arial", 20, "bold")
    )
    title_label.pack(pady=(20, 15))

    # -------------------------
    # Spending calculations
    # -------------------------

    today_spending = calculate_daily_spending()
    weekly_spending = calculate_weekly_spending()
    monthly_spending = calculate_monthly_spending()

    total_spending = sum(
        item["amount"]
        for item in expenses
    )

    total_expenses = len(expenses)

    # -------------------------
    # Spending summary
    # -------------------------

    summary_frame = ttk.LabelFrame(
        report_window,
        text="Spending Summary",
        padding=15
    )
    summary_frame.pack(
        fill="x",
        padx=20,
        pady=10
    )

    today_label = ttk.Label(
        summary_frame,
        text=f"Today: ₦{today_spending:,.2f}"
    )
    today_label.pack(
        anchor="w",
        pady=4
    )

    weekly_label = ttk.Label(
        summary_frame,
        text=f"This Week: ₦{weekly_spending:,.2f}"
    )
    weekly_label.pack(
        anchor="w",
        pady=4
    )

    monthly_label = ttk.Label(
        summary_frame,
        text=f"This Month: ₦{monthly_spending:,.2f}"
    )
    monthly_label.pack(
        anchor="w",
        pady=4
    )

    total_label = ttk.Label(
        summary_frame,
        text=f"Total Spending: ₦{total_spending:,.2f}"
    )
    total_label.pack(
        anchor="w",
        pady=4
    )

    # -------------------------
    # Expense count
    # -------------------------

    count_frame = ttk.LabelFrame(
        report_window,
        text="Expense Activity",
        padding=15
    )
    count_frame.pack(
        fill="x",
        padx=20,
        pady=10
    )

    count_label = ttk.Label(
        count_frame,
        text=f"Total Expenses: {total_expenses}"
    )
    count_label.pack(
        anchor="w"
    )

    # -------------------------
    # Category breakdown
    # -------------------------

    category_frame = ttk.LabelFrame(
        report_window,
        text="Spending By Category",
        padding=15
    )
    category_frame.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=10
    )

    category_totals = {}

    for item in expenses:
        category = item["category"]
        amount = item["amount"]

        if category not in category_totals:
            category_totals[category] = 0

        category_totals[category] += amount

    for category, amount in sorted(
        category_totals.items(),
        key=lambda item: item[1],
        reverse=True
    ):
        category_label = ttk.Label(
            category_frame,
            text=f"{category}: ₦{amount:,.2f}"
        )

        category_label.pack(
            anchor="w",
            pady=3
        )

    # -------------------------
    # Highest spending category
    # -------------------------

    highest_category = "None"

    if category_totals:
        highest_category = max(
            category_totals,
            key=category_totals.get
        )

    highest_amount = category_totals.get(
        highest_category,
        0
    )

    highest_frame = ttk.LabelFrame(
        report_window,
        text="Highest Spending Category",
        padding=15
    )
    highest_frame.pack(
        fill="x",
        padx=20,
        pady=(0, 20)
    )

    highest_label = ttk.Label(
        highest_frame,
        text=f"{highest_category}: ₦{highest_amount:,.2f}",
        font=("Arial", 11, "bold")
    )

    highest_label.pack(
        anchor="w"
    )


    
window = tk.Tk()


view_window = None
budget_window = None
set_budget_window_instance = None

window.protocol("WM_DELETE_WINDOW", confirm_exit)

window.title('Student Expense Tracker')
window.geometry('500x450')

title_label = ttk.Label(window, text = 'Student Expense Tracker', font = ('Aria', 20,'bold'))
title_label.pack(pady = (20,10))

form_frame = ttk.Frame(window)
form_frame.pack(pady=20)

expense_label = ttk.Label(
    form_frame,
    text="Expense"
)
expense_label.grid(row=0, column=0, padx=10, pady=8, sticky="w")

expense_entry = ttk.Entry(form_frame)
expense_entry.grid(row=0, column=1, padx=10, pady=8)

amount_label = ttk.Label(
    form_frame,
    text="Amount"
)
amount_label.grid(row=1, column=0, padx=10, pady=8, sticky="w")

amount_entry = ttk.Entry(form_frame)
amount_entry.grid(row=1, column=1, padx=10, pady=8)

category_label = ttk.Label(
    form_frame,
    text="Category"
)
category_label.grid(row=2, column=0, padx=10, pady=8, sticky="w")

category_entry = tk.StringVar()
category_entry.set("--Select A Category--")
category_dropdown = ttk.Combobox(
    form_frame,
    textvariable=category_entry,
    values = (
    'Food',
    'Transport',
    'Gifts',
    'Educational',
    'Utensils',
    'Accessories',
    'Schools',
    'Bills',
    'Shopping',
    'Other'
    ),
    state  = 'readonly',
    width = 20
)

category_dropdown.grid(row = 2, column=1, padx = 10, pady = 8)

button_frame = ttk.Frame(window)
button_frame.pack(pady=10)

add_expense_button = ttk.Button(
    button_frame,
    text="Add Expense",
    command=add_expense,
    width=18
)
add_expense_button.pack()

separator = ttk.Separator(
    window,
    orient="horizontal"
)
separator.pack(
    fill="x",
    padx=60,
    pady=15
)

view_frame = ttk.Frame(window)
view_frame.pack(pady=5)

view_expense_button = ttk.Button(
    view_frame,
    text="View Expenses",
    command=view_expenses,
    width=18
)
view_expense_button.pack()

budget_frame = ttk.Frame(window)
budget_frame.pack(pady = 5)

budget_button = ttk.Button(budget_frame, text = 'Set Budget', command = set_budget_window)
budget_button.pack()

view_budget_frame = ttk.Frame(window)
view_budget_frame.pack(pady=10)

view_budget_button = ttk.Button(
    view_budget_frame,
    text="View Budget",
    command=view_budget_window
)
view_budget_button.pack()

reports_frame = ttk.Frame(window)
reports_frame.pack(pady=5)

reports_button = ttk.Button(
    reports_frame,
    text="Reports",
    command=reports_window,
    width=18
)

reports_button.pack()

window.mainloop()