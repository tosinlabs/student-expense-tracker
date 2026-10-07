import csv
import json
import tkinter as tk
from pathlib import Path
from datetime import datetime, timedelta
from tkinter import filedialog, messagebox
from PIL import Image

import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# ============================================================
# APP THEME
# ============================================================

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")
ctk.set_widget_scaling(1.12)


# ============================================================
# COLORS
# ============================================================

COLORS = {
    "window": "#F7FAFD",
    "sidebar": "#FFFFFF",
    "card": "#FFFFFF",
    "border": "#DFE8F2",
    "text": "#12345B",
    "muted": "#6C8198",
    "blue": "#2388F7",
    "blue_dark": "#1764B4",
    "blue_soft": "#EAF3FF",
    "green": "#08B66A",
    "green_soft": "#E5FAF2",
    "purple": "#7A45E5",
    "purple_soft": "#F1E9FF",
    "pink": "#F23A6B",
    "pink_soft": "#FFEAF1",
    "cyan": "#13B9D0",
    "cyan_soft": "#E7FAFD",
    "orange": "#FF9F2E",
    "orange_soft": "#FFF3E3",
    "danger": "#FF4D5A",
    "danger_soft": "#FFECEE",
    "field": "#FBFDFF",
}

CATEGORY_COLORS = {
    "Food": "#FFA72C",
    "Transport": "#2987F7",
    "Educational": "#7B42DF",
    "Shopping": "#0CA56D",
    "Bills": "#F04475",
    "Entertainment": "#F6A33A",
    "Health": "#1AA9C7",
    "Gifts": "#0D9EA8",
    "Utensils": "#8244DF",
    "Accessories": "#1597A4",
    "Schools": "#7C47D7",
    "Other": "#8594A6",
}

DEFAULT_CATEGORIES = [
    "Food",
    "Transport",
    "Gifts",
    "Educational",
    "Utensils",
    "Accessories",
    "Schools",
    "Bills",
    "Shopping",
    "Other",
]


# ============================================================
# APP
# ============================================================

class ExpenseTracker(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Student Expense Tracker")
        self.geometry("1366x720")
        self.minsize(1100, 700)
        self.configure(fg_color=COLORS["window"])

        self.grid_columnconfigure(0, weight=0, minsize=155)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.data_file = Path("student_expense_tracker_data.json")
        self.feedback_file = Path("student_expense_tracker_feedback.json")
        self.categories = DEFAULT_CATEGORIES.copy()
        self.budgets = {
            "Daily": 5000.0,
            "Weekly": 20000.0,
            "Monthly": 80000.0,
        }
        self.expenses = []
        self.editing_expense_id = None
        self.current_page = "Dashboard"

        self.load_data()
        self.ensure_demo_seed_data()

        self.create_sidebar()
        self.create_main_area()
        self.bind("<Configure>", self.debug_window_size)
        self.show_page("Dashboard")


    def debug_window_size(self, event=None):
        print(
            "WINDOW:",
            self.winfo_width(),
            "x",
            self.winfo_height(),
            "| MAIN:",
            self.main_area.winfo_width(),
            "x",
            self.main_area.winfo_height(),
            "| CONTENT:",
            self.content.winfo_width(),
            "x",
            self.content.winfo_height()
        )

    
    # ========================================================
    # DATA
    # ========================================================

    def load_data(self):
        if not self.data_file.exists():
            return

        try:
            with self.data_file.open("r", encoding="utf-8") as file:
                data = json.load(file)

            self.categories = data.get("categories", DEFAULT_CATEGORIES.copy())
            self.budgets = data.get(
                "budgets",
                {"Daily": 5000.0, "Weekly": 20000.0, "Monthly": 80000.0},
            )

            self.expenses = []
            for item in data.get("expenses", []):
                self.expenses.append(
                    {
                        "id": item.get("id", self.new_id()),
                        "name": item["name"],
                        "amount": float(item["amount"]),
                        "category": item["category"],
                        "date": datetime.strptime(item["date"], "%Y-%m-%d").date(),
                    }
                )

        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError):
            self.categories = DEFAULT_CATEGORIES.copy()
            self.budgets = {"Daily": 5000.0, "Weekly": 20000.0, "Monthly": 80000.0}
            self.expenses = []

    def save_data(self):
        payload = {
            "categories": self.categories,
            "budgets": self.budgets,
            "expenses": [
                {
                    "id": expense["id"],
                    "name": expense["name"],
                    "amount": expense["amount"],
                    "category": expense["category"],
                    "date": expense["date"].isoformat(),
                }
                for expense in self.expenses
            ],
        }

        with self.data_file.open("w", encoding="utf-8") as file:
            json.dump(payload, file, indent=4)

    def ensure_demo_seed_data(self):
        """Seed the app once so the first launch resembles the reference image."""
        if self.data_file.exists() and self.expenses:
            return

        today = datetime.now().date()

        visible = [
            ("Food", 2000, today),
            ("Transport", 1500, today),
            ("Educational", 5000, today - timedelta(days=2)),
            ("Shopping", 3200, today - timedelta(days=3)),
            ("Bills", 4500, today - timedelta(days=4)),
        ]

        self.expenses = []

        for category, amount, date_value in visible:
            self.expenses.append(
                {
                    "id": self.new_id(),
                    "name": {
                        "Food": "Food",
                        "Transport": "Transport",
                        "Educational": "Educational",
                        "Shopping": "Shopping",
                        "Bills": "Bills",
                    }[category],
                    "amount": float(amount),
                    "category": category,
                    "date": date_value,
                }
            )

        self.add_demo("Food", "Snack", 2500, today - timedelta(days=5))

        month_amounts = [
            6500, 4800, 5200, 7000, 4500, 6300, 5400, 5000, 4200, 4800
        ]
        month_categories = [
            "Food", "Transport", "Educational", "Shopping", "Food",
            "Bills", "Food", "Educational", "Transport", "Shopping"
        ]
        for index, amount in enumerate(month_amounts):
            self.add_demo(
                month_categories[index],
                f"Monthly expense {index + 1}",
                amount,
                today - timedelta(days=7 + index),
            )

        old_total = 173400
        old_amounts = self.split_amount(old_total, 31)
        old_categories = [
            "Food", "Transport", "Educational", "Food", "Shopping", "Bills",
            "Food", "Educational", "Transport", "Shopping", "Food", "Other",
            "Food", "Transport", "Educational", "Shopping", "Food", "Bills",
            "Food", "Transport", "Educational", "Other", "Food", "Shopping",
            "Food", "Educational", "Transport", "Food", "Shopping", "Food", "Other"
        ]
        for index, amount in enumerate(old_amounts):
            self.add_demo(
                old_categories[index],
                f"Past expense {index + 1}",
                amount,
                today - timedelta(days=35 + index * 2),
            )

        self.budgets = {
            "Daily": 5000.0,
            "Weekly": 20000.0,
            "Monthly": 80000.0,
        }
        self.save_data()

    @staticmethod
    def split_amount(total, count):
        base = total // count
        remainder = total - base * count
        values = [base] * count
        for index in range(remainder):
            values[index] += 1
        return values

    def add_demo(self, category, name, amount, date_value):
        self.expenses.append(
            {
                "id": self.new_id(),
                "name": name,
                "amount": float(amount),
                "category": category,
                "date": date_value,
            }
        )

    @staticmethod
    def new_id():
        return f"exp_{datetime.now().timestamp()}"

    # ========================================================
    # LAYOUT
    # ========================================================

    def create_sidebar(self):
        self.sidebar = ctk.CTkFrame(
            self,
            width=155,
            corner_radius=0,
            fg_color=COLORS["sidebar"],
            border_width=1,
            border_color=COLORS["border"],
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        top_spacer = ctk.CTkFrame(self.sidebar, height=20, fg_color="transparent")
        top_spacer.pack(fill="x")

        self.nav_buttons = {}

        self.add_nav_button("dashboard.png", "Dashboard")
        self.add_nav_button("add expense.png", "Add Expense")
        self.add_nav_button("view expenses.png", "View Expenses")
        self.add_nav_button("set budget.png", "Set Budget")
        self.add_nav_button("view budget.png", "View Budget")
        self.add_nav_button("reports.png", "Reports")


        spacer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        spacer.pack(fill="both", expand=True)

        self.add_nav_button("settings.png", "Settings")
        self.add_nav_button("feedback.png", "Feedback")
        self.add_nav_button("about.png", "About")

        version = ctk.CTkLabel(
            self.sidebar,
            text="Version 2.0.0",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["muted"],
        )
        version.pack(pady=(8, 14))

    def add_nav_button(self, icon_filename, text):
        icon_image = ctk.CTkImage(
            light_image=Image.open(f"assets/{icon_filename}"),
            size=(20, 20)
        )

        button = ctk.CTkButton(
            self.sidebar,
            image=icon_image,
            text=f"   {text}",
            height=38,
            corner_radius=9,
            fg_color="transparent",
            hover_color=COLORS["blue_soft"],
            text_color="#000000",
            anchor="w",
            font=ctk.CTkFont(family="Segoe UI",size=12, weight="bold"),
            command=lambda page=text: self.show_page(page),
        )
        button.pack(fill="x", padx=9, pady=3)
        self.nav_buttons[text] = button

    def create_main_area(self):
        self.main_area = ctk.CTkFrame(
            self,
            fg_color=COLORS["window"],
            corner_radius=0,
        )
        self.main_area.grid(row=0, column=1, sticky="nsew")

        self.main_area.grid_columnconfigure(0, weight=1)
        self.main_area.grid_rowconfigure(0, weight=0)
        self.main_area.grid_rowconfigure(1, weight=1)

        self.header = ctk.CTkFrame(
            self.main_area,
            fg_color="transparent",
        )
        self.header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=20,
            pady=(13, 7),
        )
        self.header.grid_columnconfigure(1, weight=1)

        self.content = ctk.CTkFrame(
            self.main_area,
            fg_color="transparent",
        )
        self.content.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=20,
            pady=(4, 18),
        )

        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

    # ========================================================
    # COMMON HEADER
    # ========================================================

    def clear_header(self):
        for widget in self.header.winfo_children():
            widget.destroy()

    def build_dashboard_header(self):
        self.clear_header()

        title_box = ctk.CTkFrame(self.header, fg_color="transparent")
        title_box.grid(row=0, column=0, sticky="w")

        title = ctk.CTkLabel(
            title_box,
            text="Welcome Back!",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=26,
                weight="bold",
            ),
            text_color=COLORS["text"],
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            title_box,
            text="Track your expenses, stay within budget, achieve your goals.",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["muted"],
        )
        subtitle.pack(anchor="w", pady=(2, 0))

        date_card = ctk.CTkFrame(
            self.header,
            width=165,
            height=42,
            corner_radius=8,
            fg_color=COLORS["card"],
            border_width=1,
            border_color=COLORS["border"],
        )
        date_card.grid(row=0, column=2, sticky="e")
        date_card.grid_propagate(False)

        calendar_image = ctk.CTkImage(
            light_image=Image.open("assets/calendar(2).png"),
            size=(21, 21)
        )

        date_icon = ctk.CTkLabel(
            date_card,
            text="",
            image=calendar_image,
        )
        date_icon.pack(side="left", padx=(12, 8), pady=0)

        today = datetime.now().date()
        date_text_box = ctk.CTkFrame(date_card, fg_color="transparent")
        date_text_box.pack(side="left", fill="y", pady=3)

        is_today = ctk.CTkLabel(
            date_text_box,
            text="Today is",
            font=ctk.CTkFont(size=10),
            text_color=COLORS["muted"],
            height=12,
        )
        is_today.pack(anchor="w", pady=(1, 0))

        date_label = ctk.CTkLabel(
            date_text_box,
            text=today.strftime("%b %d, %Y"),
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["text"],
            height=14,
        )
        date_label.pack(anchor="w", pady=(0, 0))

    def build_standard_header(self, icon, title_text, subtitle_text, color=COLORS["blue"]):
        self.clear_header()

        icon_box = ctk.CTkFrame(
            self.header,
            width=40,
            height=40,
            corner_radius=20,
            fg_color=color,
        )
        icon_box.grid(row=0, column=0, padx=(0, 10), sticky="w")
        icon_box.grid_propagate(False)

        icon_label = ctk.CTkLabel(
            icon_box,
            text=icon,
            font=ctk.CTkFont(size=24),
            text_color="#FFFFFF",
        )
        icon_label.place(relx=0.5, rely=0.5, anchor="center")

        text_box = ctk.CTkFrame(self.header, fg_color="transparent")
        text_box.grid(row=0, column=1, sticky="w")

        title = ctk.CTkLabel(
            text_box,
            text=title_text,
            font=ctk.CTkFont(
                family="Segoe UI",
                size=20,
                weight="bold",
            ),
            text_color=COLORS["text"],
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            text_box,
            text=subtitle_text,
            font=ctk.CTkFont(size=12),
            text_color=COLORS["muted"],
        )
        subtitle.pack(anchor="w", pady=(1, 0))

    # ========================================================
    # PAGE SWITCHING
    # ========================================================

    def show_page(self, page, editing_expense_id=None):
        self.current_page = page
        self.editing_expense_id = editing_expense_id

        for widget in self.content.winfo_children():
            widget.destroy()

        for name, button in self.nav_buttons.items():
            if name == page:
                button.configure(
                    fg_color=COLORS["blue_soft"],
                    text_color="#000000",
                )
            else:
                button.configure(
                    fg_color="transparent",
                    text_color="#000000",
                )

        builders = {
            "Dashboard": self.create_dashboard_page,
            "Add Expense": self.create_add_expense_page,
            "View Expenses": self.create_view_expenses_page,
            "Set Budget": self.create_set_budget_page,
            "View Budget": self.create_view_budget_page,
            "Reports": self.create_reports_page,
            "Settings": self.create_settings_page,
            "Feedback": self.create_feedback_page,
            "About": self.create_about_page,
        }

        builders[page]()
        self.update_idletasks()

        print(
            "PAGE:", page,
            "| CONTENT:",
            self.content.winfo_width(),
            "x",
            self.content.winfo_height()
        )

    # ========================================================
    # DASHBOARD
    # ========================================================

    def create_dashboard_page(self):
        self.build_dashboard_header()

        page = ctk.CTkFrame(self.content, fg_color="transparent")
        page.pack(fill="both", expand=True)

        page.grid_columnconfigure(0, weight=3)
        page.grid_columnconfigure(1, weight=2)
        page.grid_rowconfigure(1, weight=1)

        # --------------------------------------------------------
        # SUMMARY CARDS
        # --------------------------------------------------------

        cards_frame = ctk.CTkFrame(page, fg_color="transparent")
        cards_frame.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(15, 25),
        )

        for i in range(4):
            cards_frame.grid_columnconfigure(
                i,
                weight=1,
                uniform="dashboard_card",
            )

        today_spent = self.calculate_period_spending("Daily")
        week_spent = self.calculate_period_spending("Weekly")
        month_spent = self.calculate_period_spending("Monthly")
        total_spent = self.total_spending()

        # Each card now uses a matching accent + background pair.
        self.create_summary_card(
            cards_frame,
            0,
            "Today's Spending",
            today_spent,
            "#078B5A",
            "#D8F4E8",
            "wallet.png",
        )
        self.create_summary_card(
            cards_frame,
            1,
            "This Week",
            week_spent,
            "#1764B4",
            "#DCEBFA",
            "calendar(blue).png",
        )
        self.create_summary_card(
            cards_frame,
            2,
            "This Month",
            month_spent,
            "#6336BA",
            "#E9DFFF",
            "calendar.png",
        )
        self.create_summary_card(
            cards_frame,
            3,
            "Total Spending",
            total_spent,
            "#D12F5B",
            "#F9DDE7",
            "total spending.png",
        )

        # --------------------------------------------------------
        # LOWER DASHBOARD: RECENT EXPENSES + SMART INSIGHTS
        # --------------------------------------------------------

        self.create_dashboard_table(page)
        self.create_smart_insight_card(page)

        return page

    def create_summary_card(
        self,
        parent,
        column,
        title,
        amount,
        accent,
        bg_color,
        icon_filename,
    ):
        card = ctk.CTkFrame(
            parent,
            fg_color=bg_color,
            corner_radius=10,
            border_width=1,
            border_color=accent,
            height=82,
        )
        card.grid(
            row=0,
            column=column,
            sticky="ew",
            padx=(0, 8 if column < 3 else 0),
        )
        card.grid_propagate(False)

        icon_box = ctk.CTkFrame(
            card,
            width=34,
            height=34,
            corner_radius=17,
            fg_color="#FFFFFF",
        )
        icon_box.place(x=12, y=24)
        icon_box.grid_propagate(False)

        icon_image = ctk.CTkImage(
            light_image=Image.open(f"assets/{icon_filename}"),
            size=(19, 19),
        )

        icon_label = ctk.CTkLabel(
            icon_box,
            text="",
            image=icon_image,
        )
        icon_label.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=accent,
        ).place(x=55, y=15)

        ctk.CTkLabel(
            card,
            text=self.currency(amount),
            font=ctk.CTkFont(size=17, weight="bold"),
            text_color=COLORS["text"],
        ).place(x=55, y=36)

    def create_dashboard_table(self, parent):
        """Recent Expenses panel on the left side of the dashboard."""
        table_card = ctk.CTkFrame(
            parent,
            fg_color=COLORS["card"],
            corner_radius=10,
            border_width=1,
            border_color=COLORS["border"],
        )
        table_card.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=(0, 10),
        )

        title_frame = ctk.CTkFrame(table_card, fg_color="transparent")
        title_frame.pack(
            fill="x",
            padx=14,
            pady=(12, 8),
        )

        ctk.CTkLabel(
            title_frame,
            text="Recent Expenses",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text"],
        ).pack(side="left")

        ctk.CTkButton(
            title_frame,
            text="View All",
            width=65,
            height=25,
            corner_radius=7,
            fg_color="transparent",
            hover_color=COLORS["blue_soft"],
            text_color=COLORS["blue_dark"],
            font=ctk.CTkFont(size=10, weight="bold"),
            command=lambda: self.show_page("View Expenses"),
        ).pack(side="right")

        header_row = ctk.CTkFrame(
            table_card,
            fg_color=COLORS["field"],
            height=30,
            corner_radius=6,
        )
        header_row.pack(
            fill="x",
            padx=12,
            pady=(0, 7),
        )

        columns = [
            ("Expense", "left"),
            ("Amount", "right"),
            ("Category", "right"),
            ("Date", "right"),
        ]

        for text, side in columns:
            ctk.CTkLabel(
                header_row,
                text=text,
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=COLORS["muted"],
            ).pack(
                side=side,
                padx=9,
            )

        rows_frame = ctk.CTkFrame(
            table_card,
            fg_color="transparent",
        )
        rows_frame.pack(
            fill="both",
            expand=True,
            padx=12,
            pady=(0, 10),
        )

        recent_items = sorted(
            self.expenses,
            key=lambda expense: expense["date"],
            reverse=True,
        )[:5]

        if not recent_items:
            ctk.CTkLabel(
                rows_frame,
                text="No expenses recorded yet.",
                font=ctk.CTkFont(size=12),
                text_color=COLORS["muted"],
            ).pack(pady=20)
            return

        for index, exp in enumerate(recent_items):
            if index > 0:
                ctk.CTkFrame(
                    rows_frame,
                    height=1,
                    fg_color=COLORS["border"],
                ).pack(fill="x", pady=2)

            row = ctk.CTkFrame(
                rows_frame,
                fg_color="transparent",
                height=32,
            )
            row.pack(fill="x", pady=2)

            ctk.CTkLabel(
                row,
                text=exp["name"],
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=COLORS["text"],
            ).pack(side="left", padx=5)

            ctk.CTkLabel(
                row,
                text=exp["date"].strftime("%b %d, %Y"),
                font=ctk.CTkFont(size=10),
                text_color=COLORS["muted"],
            ).pack(side="right", padx=4)

            ctk.CTkLabel(
                row,
                text=exp["category"],
                font=ctk.CTkFont(size=10),
                text_color=COLORS["text"],
            ).pack(side="right", padx=6)

            ctk.CTkLabel(
                row,
                text=self.currency(exp["amount"]),
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=COLORS["text"],
            ).pack(side="right", padx=6)

    def create_smart_insight_card(self, parent):
        """Smart Insights panel on the right side of the dashboard."""
        card = ctk.CTkFrame(
            parent,
            fg_color=COLORS["card"],
            corner_radius=10,
            border_width=1,
            border_color=COLORS["border"],
        )
        card.grid(
            row=1,
            column=1,
            sticky="nsew",
            padx=(10, 0),
        )

        heading = ctk.CTkFrame(card, fg_color="transparent")
        heading.pack(
            fill="x",
            padx=14,
            pady=(12, 10),
        )

        ctk.CTkLabel(
            heading,
            text="Smart Insights",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text"],
        ).pack(side="left")

        insight_title, insight_text, tip_text, color, bg_color = self.get_financial_insight()

        box = ctk.CTkFrame(
            card,
            fg_color=bg_color,
            corner_radius=8,
        )
        box.pack(
            fill="x",
            padx=12,
            pady=6,
        )

        ctk.CTkLabel(
            box,
            text=insight_title,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=color,
        ).pack(
            anchor="w",
            padx=12,
            pady=(10, 3),
        )

        ctk.CTkLabel(
            box,
            text=insight_text,
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text"],
            wraplength=250,
            justify="left",
        ).pack(
            anchor="w",
            padx=12,
            pady=(0, 10),
        )

        tip_box = ctk.CTkFrame(
            card,
            fg_color=COLORS["field"],
            corner_radius=8,
            border_width=1,
            border_color=COLORS["border"],
        )
        tip_box.pack(
            fill="both",
            expand=True,
            padx=12,
            pady=(6, 12),
        )

        ctk.CTkLabel(
            tip_box,
            text="💡 Quick Tip",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["blue_dark"],
        ).pack(
            anchor="w",
            padx=12,
            pady=(10, 3),
        )

        ctk.CTkLabel(
            tip_box,
            text=tip_text,
            font=ctk.CTkFont(size=11),
            text_color=COLORS["muted"],
            wraplength=250,
            justify="left",
        ).pack(
            anchor="w",
            padx=12,
            pady=(0, 10),
        )

    def get_financial_insight(self):
        """Analyzes expenses to generate dynamic feedback."""
        today = datetime.now().date()
        this_week_spent = self.calculate_period_spending("Weekly")
        weekly_budget = self.budgets.get("Weekly", 20000.0)

        budget_ratio = (this_week_spent / weekly_budget) if weekly_budget > 0 else 0

        week_start = today - timedelta(days=today.weekday())
        week_expenses = [e for e in self.expenses if week_start <= e["date"] <= today]

        cat_totals = {}
        for e in week_expenses:
            cat_totals[e["category"]] = cat_totals.get(e["category"], 0) + e["amount"]

        top_cat = max(cat_totals, key=cat_totals.get) if cat_totals else None

        if budget_ratio >= 1.0:
            title = "⚠️ Budget Limit Reached"
            text = f"You've spent {self.currency(this_week_spent)}, exceeding your weekly budget of {self.currency(weekly_budget)}."
            tip = "Try holding off on non-essential expenses until next week begins."
            color = COLORS["danger"]
            bg_color = COLORS["danger_soft"]
        elif budget_ratio >= 0.75:
            title = "⚡ High Spending Warning"
            text = f"You have used {budget_ratio*100:.0f}% of your weekly budget ({self.currency(this_week_spent)} spent)."
            tip = "Monitor daily micro-purchases to prevent going over budget."
            color = COLORS["orange"]
            bg_color = COLORS["orange_soft"]
        elif top_cat:
            top_amount = cat_totals[top_cat]
            title = f"📊 Primary Expense: {top_cat}"
            text = f"{top_cat} makes up {self.currency(top_amount)} of your spending this week."
            tip = f"Setting a specific spending limit for {top_cat} can help keep total costs down."
            color = COLORS["blue_dark"]
            bg_color = COLORS["blue_soft"]
        else:
            title = "🎉 Healthy Balance"
            text = f"You've spent {self.currency(this_week_spent)} out of {self.currency(weekly_budget)} this week."
            tip = "Great job managing your spending! Put remaining funds into a savings goal."
            color = COLORS["green"]
            bg_color = COLORS["green_soft"]

        return title, text, tip, color, bg_color



    # ========================================================
    # ADD EXPENSE PAGE
    # ========================================================

    def create_add_expense_page(self):

        # Header
        self.build_standard_header(
            "+",
            "Add Expense",
            "Keep track of your daily expenses.",
            COLORS["green"],
        )

        # Main card
        card = ctk.CTkFrame(
            self.content,
            fg_color=COLORS["card"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"],
        )
        card.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=0,
            pady=0
        )

        card.grid_rowconfigure(0, weight=1)
        card.grid_columnconfigure(0, weight=1)

        # Inner container
        inner = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )
        inner.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=22,
            pady=18
        )

        inner.grid_columnconfigure(0, weight=1)

        # --------------------------------------------------
        # EXPENSE NAME
        # --------------------------------------------------

        self.add_form_label_grid(
            inner,
            "Expense",
            row=0
        )
        self.expense_name_entry = ctk.CTkEntry(
            inner,
            height=36,
            placeholder_text="Expense name",
            fg_color=COLORS["field"],
            border_color=COLORS["border"],
            text_color=COLORS["text"],
        )
        self.expense_name_entry.grid(
            row=1,
            column=0,
            sticky="ew",
            pady=(0, 8)
        )

        # --------------------------------------------------
        # AMOUNT
        # --------------------------------------------------

        self.add_form_label_grid(
            inner,
            "Amount",
            row=2
        )

        self.expense_amount_entry = ctk.CTkEntry(
            inner,
            height=36,
            placeholder_text="2500",
            fg_color=COLORS["field"],
            border_color=COLORS["border"],
            text_color=COLORS["text"],
        )
        self.expense_amount_entry.grid(
            row=3,
            column=0,
            sticky="ew",
            pady=(0, 8)
        )

        # --------------------------------------------------
        # CATEGORY
        # --------------------------------------------------

        self.add_form_label_grid(
            inner,
            "Category",
            row=4
        )

        self.expense_category_menu = ctk.CTkOptionMenu(
            inner,
            height=36,
            corner_radius=7,
            values=self.categories,
            fg_color=COLORS["field"],
            button_color=COLORS["blue"],
            button_hover_color=COLORS["blue_dark"],
            text_color=COLORS["text"],
            dropdown_fg_color=COLORS["card"],
            dropdown_text_color=COLORS["text"],
        )
        self.expense_category_menu.grid(
            row=5,
            column=0,
            sticky="ew",
            pady=(0, 8)
        )

        self.expense_category_menu.set(
            self.categories[0]
        )

        # --------------------------------------------------
        # DATE
        # --------------------------------------------------

        self.add_form_label_grid(
            inner,
            "Date",
            row=6
        )

        self.expense_date_entry = ctk.CTkEntry(
            inner,
            height=36,
            placeholder_text="DD/MM/YYYY",
            fg_color=COLORS["field"],
            border_color=COLORS["border"],
            text_color=COLORS["text"],
        )
        self.expense_date_entry.grid(
            row=7,
            column=0,
            sticky="ew",
            pady=(0, 8)
        )

        current_date = datetime.now().date()

        self.expense_date_entry.insert(
            0,
            current_date.strftime("%d/%m/%Y")
        )

        # --------------------------------------------------
        # EDIT MODE / BUTTON TEXT
        # --------------------------------------------------

        if self.editing_expense_id:
            self.populate_expense_form(
                self.editing_expense_id
            )
            button_text = "Save Changes"
        else:
            button_text = "Add Expense"

        # --------------------------------------------------
        # ACTION BUTTONS
        # --------------------------------------------------

        buttons = ctk.CTkFrame(
            inner,
            fg_color="transparent"
        )
        buttons.grid(
            row=8,
            column=0,
            sticky="ew",
            pady=(28, 0)
        )

        buttons.grid_columnconfigure(
            0,
            weight=3
        )

        buttons.grid_columnconfigure(
            1,
            weight=1
        )

        # Add Expense / Save Changes
        ctk.CTkButton(
            buttons,
            text=button_text,
            height=38,
            corner_radius=8,
            fg_color=COLORS["green"],
            hover_color="#079A5A",
            text_color="#FFFFFF",
            font=ctk.CTkFont(
                size=13,
                weight="bold"
            ),
            command=self.save_expense_from_form,
        ).grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 6)
        )

        # Clear
        ctk.CTkButton(
            buttons,
            text="Clear",
            height=38,
            corner_radius=8,
            fg_color=COLORS["blue_soft"],
            hover_color="#D8E9FC",
            text_color=COLORS["blue_dark"],
            font=ctk.CTkFont(
                size=13
            ),
            command=self.clear_expense_form,
        ).grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(6, 0)
        )

    def add_form_label_grid(self, parent, text, row):
        label = ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS["text"],
        )
        label.grid(row=row, column=0, sticky="w", pady=(10, 4))

    def populate_expense_form(self, expense_id):
        expense = self.find_expense(expense_id)
        if not expense:
            return

        self.expense_name_entry.insert(0, expense["name"])
        self.expense_amount_entry.insert(0, str(int(expense["amount"]) if expense["amount"].is_integer() else expense["amount"]))
        self.expense_category_menu.set(expense["category"])
        self.expense_date_entry.delete(0, "end")
        self.expense_date_entry.insert(0, expense["date"].strftime("%d/%m/%Y"))

    def clear_expense_form(self):
        self.expense_name_entry.delete(0, "end")
        self.expense_amount_entry.delete(0, "end")
        self.expense_date_entry.delete(0, "end")
        self.expense_date_entry.insert(0, datetime.now().date().strftime("%d/%m/%Y"))
        self.expense_category_menu.set(self.categories[0])
        
        
    def save_expense_from_form(self):

        name = self.expense_name_entry.get().strip()

        amount_raw = self.expense_amount_entry.get().strip().replace(",", "")

        category = self.expense_category_menu.get()

        date_raw = self.expense_date_entry.get().strip()

        # Check expense name
        if not name:
            messagebox.showerror(
                "Add Expense",
                "Please enter an expense name.",
                parent=self
            )
            return

        # Expense name must not contain digits
        if any(char.isdigit() for char in name):
            messagebox.showwarning(
                "Invalid Expense Name",
                "Expense name can only contain letters and symbols.",
                parent=self
            )
            return

        # Check amount
        try:
            amount = float(amount_raw)

            if amount <= 0:
                raise ValueError

        except ValueError:
            messagebox.showerror(
                "Add Expense",
                "Please enter a valid amount.",
                parent=self
            )
            return

        # Check date
        try:
            date_value = datetime.strptime(
                date_raw,
                "%d/%m/%Y"
            ).date()

        except ValueError:
            messagebox.showerror(
                "Add Expense",
                "Date must use DD/MM/YYYY.",
                parent=self
            )
            return

        # Edit existing expense
        if self.editing_expense_id:

            expense = self.find_expense(
                self.editing_expense_id
            )

            if expense:
                expense.update({
                    "name": name,
                    "amount": amount,
                    "category": category,
                    "date": date_value,
                })

        # Add new expense
        else:

            self.expenses.append({
                "id": self.new_id(),
                "name": name,
                "amount": amount,
                "category": category,
                "date": date_value,
            })

        # Save data
        self.save_data()

        self.editing_expense_id = None

        self.show_page("Dashboard")

    # ========================================================
    # VIEW EXPENSES PAGE
    # ========================================================

    def create_view_expenses_page(self):

        self.build_standard_header(
            "▤",
            "View Expenses",
            "View, search, and manage your expenses.",
            COLORS["blue"],
        )

        # Main card
        card = ctk.CTkFrame(
            self.content,
            fg_color=COLORS["card"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"],
        )
        card.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        card.grid_rowconfigure(1, weight=1)
        card.grid_columnconfigure(0, weight=1)

        # --------------------------------------------------
        # SEARCH / FILTER / SORT
        # --------------------------------------------------

        controls = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )
        controls.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=18,
            pady=(16, 12)
        )

        controls.grid_columnconfigure(
            0,
            weight=1
        )

        # Search box
        self.search_entry = ctk.CTkEntry(
            controls,
            height=38,
            placeholder_text="Search expenses...",
            fg_color=COLORS["field"],
            border_color=COLORS["border"],
            text_color=COLORS["text"],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=13
            ),
        )
        self.search_entry.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 8)
        )

        self.search_entry.bind(
            "<KeyRelease>",
            lambda _event: self.refresh_expense_table()
        )

        # Category filter
        categories = ["All Categories"] + self.categories

        self.filter_menu = ctk.CTkOptionMenu(
            controls,
            width=165,
            height=38,
            values=categories,
            fg_color=COLORS["field"],
            button_color=COLORS["blue"],
            button_hover_color=COLORS["blue_dark"],
            text_color=COLORS["text"],
            dropdown_fg_color=COLORS["card"],
            dropdown_text_color=COLORS["text"],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=13
            ),
            dropdown_font=ctk.CTkFont(
                family="Segoe UI",
                size=13
            ),
            command=lambda _value: self.refresh_expense_table(),
        )
        self.filter_menu.grid(
            row=0,
            column=1,
            padx=8
        )

        self.filter_menu.set(
            "All Categories"
        )

        # Sort menu
        self.sort_menu = ctk.CTkOptionMenu(
            controls,
            width=175,
            height=38,
            values=[
                "Date (Newest)",
                "Date (Oldest)",
                "Amount (High to Low)",
                "Amount (Low to High)",
            ],
            fg_color=COLORS["field"],
            button_color=COLORS["blue"],
            button_hover_color=COLORS["blue_dark"],
            text_color=COLORS["text"],
            dropdown_fg_color=COLORS["card"],
            dropdown_text_color=COLORS["text"],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=13
            ),
            dropdown_font=ctk.CTkFont(
                family="Segoe UI",
                size=13
            ),
            command=lambda _value: self.refresh_expense_table(),
        )
        self.sort_menu.grid(
            row=0,
            column=2,
            padx=(8, 0)
        )

        self.sort_menu.set(
            "Date (Newest)"
        )

        # --------------------------------------------------
        # EXPENSE TABLE
        # --------------------------------------------------

        table_wrap = ctk.CTkScrollableFrame(
            card,
            fg_color=COLORS["field"],
            corner_radius=8,
        )
        table_wrap.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=18,
            pady=(0, 10)
        )

        self.expense_table_wrap = table_wrap

        # --------------------------------------------------
        # FOOTER
        # --------------------------------------------------

        footer = ctk.CTkFrame(
            card,
            fg_color="transparent"
        )
        footer.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=18,
            pady=(0, 14)
        )

        self.total_spent_label = ctk.CTkLabel(
            footer,
            text="",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=13,
                weight="bold"
            ),
            text_color=COLORS["text"],
        )
        self.total_spent_label.pack(
            side="right"
        )

        self.refresh_expense_table()

    def refresh_expense_table(self):

        if not hasattr(self, "expense_table_wrap"):
            return

        # Clear existing table
        for widget in self.expense_table_wrap.winfo_children():
            widget.destroy()

        # --------------------------------------------------
        # SEARCH / FILTER / SORT
        # --------------------------------------------------

        query = self.search_entry.get().strip().lower()
        category = self.filter_menu.get()
        sort_mode = self.sort_menu.get()

        filtered = []

        for expense in self.expenses:

            # Ignore old/sample expenses labelled "Past Expense"
            expense_name_lower = expense["name"].strip().lower()

            if "past expense" in expense_name_lower:
                continue

            matches_query = (
                query in expense["name"].lower()
                or query in expense["category"].lower()
            )

            matches_category = (
                category == "All Categories"
                or expense["category"] == category
            )

            if matches_query and matches_category:
                filtered.append(expense)

        # --------------------------------------------------
        # SORTING
        # --------------------------------------------------

        if sort_mode == "Date (Newest)":

            filtered.sort(
                key=lambda item: item["date"],
                reverse=True
            )

        elif sort_mode == "Date (Oldest)":

            filtered.sort(
                key=lambda item: item["date"]
            )

        elif sort_mode == "Amount (High to Low)":

            filtered.sort(
                key=lambda item: item["amount"],
                reverse=True
            )

        else:

            filtered.sort(
                key=lambda item: item["amount"]
            )

        # --------------------------------------------------
        # TABLE HEADERS
        # --------------------------------------------------

        headers = [
            "Expense",
            "Amount",
            "Category",
            "Date",
            "Actions"
        ]

        widths = [3, 2, 2, 2, 1]

        for index, (text, weight) in enumerate(
            zip(headers, widths)
        ):

            self.expense_table_wrap.grid_columnconfigure(
                index,
                weight=weight
            )

            ctk.CTkLabel(
                self.expense_table_wrap,
                text=text,
                font=ctk.CTkFont(
                    family="Segoe UI",
                    size=13,
                    weight="bold"
                ),
                text_color=COLORS["text"],
            ).grid(
                row=0,
                column=index,
                sticky="w",
                padx=8,
                pady=(8, 10)
            )

        # --------------------------------------------------
        # EXPENSE ROWS
        # --------------------------------------------------

        for row_index, expense in enumerate(
            filtered,
            start=1
        ):

            color = CATEGORY_COLORS.get(
                expense["category"],
                COLORS["blue"]
            )

            # Category dot
            dot = tk.Canvas(
                self.expense_table_wrap,
                width=14,
                height=14,
                highlightthickness=0,
                bg=COLORS["field"],
            )

            dot.create_oval(
                3,
                3,
                11,
                11,
                fill=color,
                outline=color
            )

            dot.grid(
                row=row_index,
                column=0,
                sticky="w",
                padx=(8, 0)
            )

            # Expense name
            ctk.CTkLabel(
                self.expense_table_wrap,
                text=expense["name"],
                font=ctk.CTkFont(
                    family="Segoe UI",
                    size=13
                ),
                text_color=COLORS["text"],
            ).grid(
                row=row_index,
                column=0,
                sticky="w",
                padx=(27, 6),
                pady=7
            )

            # Amount
            ctk.CTkLabel(
                self.expense_table_wrap,
                text=self.currency(expense["amount"]),
                font=ctk.CTkFont(
                    family="Segoe UI",
                    size=13,
                    weight="bold"
                ),
                text_color=COLORS["text"],
            ).grid(
                row=row_index,
                column=1,
                sticky="w",
                padx=8,
                pady=7
            )

            # Category
            ctk.CTkLabel(
                self.expense_table_wrap,
                text=expense["category"],
                font=ctk.CTkFont(
                    family="Segoe UI",
                    size=13
                ),
                text_color=COLORS["text"],
            ).grid(
                row=row_index,
                column=2,
                sticky="w",
                padx=8,
                pady=7
            )

            # Date
            ctk.CTkLabel(
                self.expense_table_wrap,
                text=expense["date"].strftime(
                    "%b %d, %Y"
                ),
                font=ctk.CTkFont(
                    family="Segoe UI",
                    size=13
                ),
                text_color=COLORS["text"],
            ).grid(
                row=row_index,
                column=3,
                sticky="w",
                padx=8,
                pady=7
            )

            # --------------------------------------------------
            # ACTION BUTTONS
            # --------------------------------------------------

            actions = ctk.CTkFrame(
                self.expense_table_wrap,
                fg_color="transparent"
            )

            actions.grid(
                row=row_index,
                column=4,
                sticky="w",
                padx=6,
                pady=5
            )

            # Edit
            ctk.CTkButton(
                actions,
                text="Edit",
                width=52,
                height=30,
                corner_radius=7,
                fg_color=COLORS["blue_soft"],
                hover_color="#D9EAFE",
                text_color=COLORS["blue"],
                font=ctk.CTkFont(
                    family="Segoe UI",
                    size=12,
                    weight="bold"
                ),
                command=lambda expense_id=expense["id"]:
                    self.show_page(
                        "Add Expense",
                        expense_id
                    ),
            ).pack(
                side="left",
                padx=(0, 5)
            )

            # Delete
            ctk.CTkButton(
                actions,
                text="Delete",
                width=58,
                height=30,
                corner_radius=7,
                fg_color=COLORS["danger_soft"],
                hover_color="#FFD9DF",
                text_color=COLORS["danger"],
                font=ctk.CTkFont(
                    family="Segoe UI",
                    size=12,
                    weight="bold"
                ),
                command=lambda expense_id=expense["id"]:
                    self.delete_expense(expense_id),
            ).pack(
                side="left"
            )

        # --------------------------------------------------
        # TOTAL
        # --------------------------------------------------

        total = sum(
            item["amount"]
            for item in filtered
        )

        self.total_spent_label.configure(
            text=(
                f"Total Amount Spent:   "
                f"{self.currency(total)}"
            )
        )

    def delete_expense(self, expense_id):
        expense = self.find_expense(expense_id)
        if not expense:
            return

        confirmed = messagebox.askyesno(
            "Delete Expense",
            f"Delete '{expense['name']}'?",
            parent=self,
        )
        if not confirmed:
            return

        self.expenses = [item for item in self.expenses if item["id"] != expense_id]
        self.save_data()
        self.show_page("View Expenses")

    # ========================================================
    # SET BUDGET PAGE
    # ========================================================

    def create_set_budget_page(self):
        self.build_standard_header(
            "✓",
            "Set Budget",
            "Set your daily, weekly and monthly budgets.",
            COLORS["blue"],
        )

        card = ctk.CTkFrame(
            self.content,
            fg_color=COLORS["card"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"],
        )
        card.grid(row=0, column=0, sticky="nsew")

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=25, pady=23)

        fields = {}
        for period in ["Daily", "Weekly", "Monthly"]:
            self.add_form_label(inner, f"{period} Budget (₦)")
            entry = ctk.CTkEntry(
                inner,
                height=38,
                fg_color=COLORS["field"],
                border_color=COLORS["border"],
            )
            entry.pack(fill="x", pady=(0, 4))
            entry.insert(0, str(int(self.budgets.get(period, 0))))
            fields[period] = entry

        buttons = ctk.CTkFrame(inner, fg_color="transparent")
        buttons.pack(fill="x", side="bottom", pady=(28, 0))
        buttons.grid_columnconfigure(0, weight=3)
        buttons.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            buttons,
            text="Save Budget",
            height=38,
            corner_radius=8,
            fg_color=COLORS["green"],
            hover_color="#079A5A",
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=lambda: self.save_budgets(fields),
        ).grid(row=0, column=0, sticky="ew", padx=(0, 6))

        ctk.CTkButton(
            buttons,
            text="Cancel",
            height=38,
            corner_radius=8,
            fg_color=COLORS["blue_soft"],
            hover_color="#D9EAFE",
            text_color=COLORS["blue_dark"],
            font=ctk.CTkFont(size=13),
            command=lambda: self.show_page("View Budget"),
        ).grid(row=0, column=1, sticky="ew", padx=(6, 0))

    def save_budgets(self, fields):
        new_values = {}
        for period, entry in fields.items():
            raw = entry.get().strip().replace(",", "")
            try:
                value = float(raw)
                if value <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Set Budget", f"Enter a valid {period.lower()} budget.", parent=self)
                return
            new_values[period] = value

        self.budgets.update(new_values)
        self.save_data()
        self.show_page("View Budget")

    # ========================================================
    # VIEW BUDGET PAGE
    # ========================================================

    def create_view_budget_page(self):

        self.build_standard_header(
            "▥",
            "View Budget",
            "See how you're doing with your budget.",
            COLORS["blue"],
        )

        page = self.content

        page.grid_columnconfigure(
            0,
            weight=1
        )

        page.grid_rowconfigure(
            0,
            weight=1
        )

        # Main budget cards container
        cards = ctk.CTkFrame(
            page,
            fg_color="transparent"
        )

        cards.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        cards.grid_columnconfigure(
            0,
            weight=1
        )

        cards.grid_rowconfigure(
            0,
            weight=1
        )

        cards.grid_rowconfigure(
            1,
            weight=1
        )

        cards.grid_rowconfigure(
            2,
            weight=1
        )

        # --------------------------------------------------
        # BUDGET CARD STYLES
        # --------------------------------------------------

        styles = [
            (
                "Daily",
                COLORS["green_soft"],
                COLORS["green"],
                "assets/calendar(green).png"
            ),
            (
                "Weekly",
                COLORS["blue_soft"],
                COLORS["blue"],
                "assets/calendar(blue).png"
            ),
            (
                "Monthly",
                COLORS["purple_soft"],
                COLORS["purple"],
                "assets/calendar.png"
            ),
        ]

        # --------------------------------------------------
        # CREATE BUDGET CARDS
        # --------------------------------------------------

        for row_index, (
            period,
            bg,
            accent,
            icon_file
        ) in enumerate(styles):

            self.create_budget_status_card(
                cards,
                period,
                bg,
                accent,
                icon_file,
                row_index
            )

    def create_budget_status_card(
        self,
        parent,
        period,
        background,
        accent,
        icon,
        row
    ):

        # --------------------------------------------------
        # CARD
        # --------------------------------------------------

        card = ctk.CTkFrame(
            parent,
            fg_color=background,
            corner_radius=12,
            border_width=1,
            border_color=accent,
        )

        card.grid(
            row=row,
            column=0,
            sticky="nsew",
            pady=(0, 10 if row < 2 else 0)
        )

        card.grid_columnconfigure(
            0,
            weight=1
        )

        card.grid_columnconfigure(
            1,
            weight=0
        )

        card.grid_rowconfigure(
            0,
            weight=1
        )

        # --------------------------------------------------
        # ICON
        # --------------------------------------------------

        icon_box = ctk.CTkFrame(
            card,
            width=46,
            height=46,
            corner_radius=11,
            fg_color="#FFFFFF"
        )

        icon_box.place(
            x=18,
            y=18
        )

        icon_box.grid_propagate(False)

        # Load PNG icon
        try:

            icon_image = ctk.CTkImage(
                light_image=Image.open(icon),
                dark_image=Image.open(icon),
                size=(25, 25)
            )

            ctk.CTkLabel(
                icon_box,
                text="",
                image=icon_image
            ).place(
                relx=0.5,
                rely=0.5,
                anchor="center"
            )

        except Exception:

            # Fallback if the image can't be loaded
            ctk.CTkLabel(
                icon_box,
                text="₦",
                font=ctk.CTkFont(
                    size=18,
                    weight="bold"
                ),
                text_color=accent
            ).place(
                relx=0.5,
                rely=0.5,
                anchor="center"
            )

        # --------------------------------------------------
        # PERIOD TITLE
        # --------------------------------------------------

        ctk.CTkLabel(
            card,
            text=period,
            font=ctk.CTkFont(
                family="Segoe UI",
                size=16,
                weight="bold"
            ),
            text_color=accent,
        ).place(
            x=78,
            y=18
        )

        # --------------------------------------------------
        # BUDGET VALUES
        # --------------------------------------------------

        budget = self.budgets.get(
            period,
            0
        )

        spent = self.calculate_period_spending(
            period
        )

        remaining = budget - spent

        ratio = (
            spent / budget
            if budget
            else 0
        )

        ratio_for_ring = max(
            0,
            min(ratio, 1)
        )

        # --------------------------------------------------
        # BUDGET
        # --------------------------------------------------

        ctk.CTkLabel(
            card,
            text="Budget",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=12
            ),
            text_color=COLORS["muted"],
        ).place(
            x=78,
            y=50
        )

        ctk.CTkLabel(
            card,
            text=self.currency(budget),
            font=ctk.CTkFont(
                family="Segoe UI",
                size=14,
                weight="bold"
            ),
            text_color=COLORS["text"],
        ).place(
            x=135,
            y=48
        )

        # --------------------------------------------------
        # SPENT
        # --------------------------------------------------

        ctk.CTkLabel(
            card,
            text="Spent",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=12
            ),
            text_color=COLORS["muted"],
        ).place(
            x=78,
            y=77
        )

        ctk.CTkLabel(
            card,
            text=self.currency(spent),
            font=ctk.CTkFont(
                family="Segoe UI",
                size=14,
                weight="bold"
            ),
            text_color=COLORS["text"],
        ).place(
            x=135,
            y=75
        )

        # --------------------------------------------------
        # REMAINING
        # --------------------------------------------------

        remaining_text = (
            self.currency(abs(remaining))
            if remaining >= 0
            else f"-{self.currency(abs(remaining))}"
        )

        remaining_color = (
            COLORS["green"]
            if remaining >= 0
            else COLORS["danger"]
        )

        ctk.CTkLabel(
            card,
            text="Remaining",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=12,
                weight="bold"
            ),
            text_color=remaining_color,
        ).place(
            x=78,
            y=104
        )

        ctk.CTkLabel(
            card,
            text=remaining_text,
            font=ctk.CTkFont(
                family="Segoe UI",
                size=14,
                weight="bold"
            ),
            text_color=remaining_color,
        ).place(
            x=155,
            y=102
        )

        # --------------------------------------------------
        # PROGRESS RING
        # --------------------------------------------------

        self.draw_progress_ring(
            card,
            ratio_for_ring,
            accent,
            0,
            0
        )

    def draw_progress_ring(self, parent, ratio, accent, x, y):

        canvas = tk.Canvas(
            parent,
            width=110,
            height=110,
            bg=parent.cget("fg_color"),
            highlightthickness=0
        )

        canvas.place(
            relx=0.90,
            rely=0.5,
            anchor="center"
        )

        canvas.create_oval(
            9,
            9,
            101,
            101,
            outline="#D7E1EB",
            width=7
        )

        canvas.create_arc(
            9,
            9,
            101,
            101,
            start=90,
            extent=-360 * ratio,
            style="arc",
            outline=accent,
            width=7,
        )

        canvas.create_text(
            55,
            55,
            text=f"{ratio * 100:.0f}%",
            fill=accent,
            font=("Segoe UI", 15, "bold"),
        )

    # ========================================================
    # REPORTS PAGE
    # ========================================================

    def create_reports_page(self):
        self.build_standard_header(
            "▥",
            "Reports",
            "Get insights into your spending habits.",
            COLORS["blue"],
        )

        page = self.content
        page.grid_columnconfigure(0, weight=1)
        page.grid_columnconfigure(1, weight=2)
        page.grid_rowconfigure(0, weight=1)
        page.grid_rowconfigure(1, weight=1)

        summary_card = self.create_report_card(page, "Spending Summary", 0, 0, 1, 1)
        self.fill_spending_summary(summary_card)

        category_card = self.create_report_card(page, "Spending By Category", 0, 1, 1, 1)
        self.fill_category_report(category_card)

        activity_card = self.create_report_card(page, "Expense Activity", 1, 0, 1, 1)
        self.fill_expense_activity(activity_card)

        highest_card = self.create_report_card(page, "Highest Spending Category", 1, 1, 1, 1)
        self.fill_highest_category(highest_card)

    def create_report_card(self, parent, title, row, column, rowspan, colspan):
        card = ctk.CTkFrame(
            parent,
            fg_color=COLORS["card"],
            corner_radius=10,
            border_width=1,
            border_color=COLORS["border"],
        )
        card.grid(row=row, column=column, rowspan=rowspan, columnspan=colspan, sticky="nsew", padx=(0 if column == 0 else 8, 8 if column == 0 else 0), pady=(0 if row == 0 else 8, 8 if row == 0 else 0))
        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["text"],
        ).pack(anchor="w", padx=10, pady=(10, 7))
        return card

    def fill_spending_summary(self, card):
        rows = [
            ("▣", "Today", self.calculate_period_spending("Daily"), COLORS["green"]),
            ("▣", "This Week", self.calculate_period_spending("Weekly"), COLORS["blue"]),
            ("▣", "This Month", self.calculate_period_spending("Monthly"), COLORS["purple"]),
            ("◍", "Total Spending", self.total_spending(), COLORS["pink"]),
        ]
        for icon, label, amount, color in rows:
            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=4)
            ctk.CTkLabel(row, text=icon, font=ctk.CTkFont(size=12), text_color=color).pack(side="left")
            ctk.CTkLabel(row, text=label, font=ctk.CTkFont(size=10), text_color=COLORS["muted"]).pack(side="left", padx=5)
            ctk.CTkLabel(row, text=self.currency(amount), font=ctk.CTkFont(size=10, weight="bold"), text_color=COLORS["text"]).pack(side="right")

    def fill_category_report(self, card):
        chart_frame = ctk.CTkFrame(card, fg_color="transparent")
        chart_frame.pack(fill="both", expand=True, padx=8, pady=2)
        chart_frame.grid_columnconfigure(0, weight=1)
        chart_frame.grid_columnconfigure(1, weight=1)
        chart_frame.grid_rowconfigure(0, weight=1)

        totals = self.category_totals()
        if not totals:
            totals = {"Other": 1}

        labels = list(totals.keys())
        values = list(totals.values())
        palette = [CATEGORY_COLORS.get(label, "#9AA8B6") for label in labels]

        figure = Figure(figsize=(2.8, 1.8), dpi=100)
        axis = figure.add_subplot(111)
        axis.pie(
            values,
            startangle=90,
            counterclock=False,
            colors=palette,
            wedgeprops={"width": 0.34, "edgecolor": "white"},
        )
        total = sum(values)
        axis.text(0, 0.05, self.currency(total, decimals=0).replace(".00", ""), ha="center", va="center", fontsize=15, color=COLORS["text"], fontweight="bold")
        axis.text(0, -0.15, "Total", ha="center", va="center", fontsize=12, color=COLORS["muted"])
        axis.axis("equal")
        figure.tight_layout(pad=1)

        canvas = FigureCanvasTkAgg(figure, master=chart_frame)
        canvas.draw()

        chart_widget = canvas.get_tk_widget()
        chart_widget.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=10,
            pady=10
        )

        chart_frame.grid_rowconfigure(0, weight=1)
        chart_frame.grid_columnconfigure(0, weight=1)

        legend = ctk.CTkScrollableFrame(chart_frame, fg_color="transparent")
        legend.grid(row=0, column=1, sticky="nsew", padx=(0, 4), pady=2)

        for label, value in sorted(totals.items(), key=lambda item: item[1], reverse=True):
            color = CATEGORY_COLORS.get(label, "#9AA8B6")
            pct = value / total * 100 if total else 0
            row = ctk.CTkFrame(legend, fg_color="transparent")
            row.pack(fill="x", pady=2)
            dot = tk.Canvas(row, width=10, height=10, highlightthickness=0, bg=COLORS["card"])
            dot.create_oval(2, 2, 8, 8, fill=color, outline=color)
            dot.pack(side="left")
            ctk.CTkLabel(row, text=label, font=ctk.CTkFont(size=9), text_color=COLORS["text"]).pack(side="left", padx=4)
            ctk.CTkLabel(row, text=self.currency(value), font=ctk.CTkFont(size=9), text_color=COLORS["text"]).pack(side="left", padx=4)
            ctk.CTkLabel(row, text=f"{pct:.1f}%", font=ctk.CTkFont(size=9), text_color=COLORS["muted"]).pack(side="right")

    def fill_expense_activity(self, card):
        total_count = len(self.expenses)
        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=10, pady=(20, 0))
        ctk.CTkLabel(row, text="◌", font=ctk.CTkFont(size=13), text_color=COLORS["muted"]).pack(side="left")
        ctk.CTkLabel(row, text="Total Expenses", font=ctk.CTkFont(size=10), text_color=COLORS["muted"]).pack(side="left", padx=6)
        ctk.CTkLabel(row, text=str(total_count), font=ctk.CTkFont(size=13, weight="bold"), text_color=COLORS["text"]).pack(side="right")

    def fill_highest_category(self, card):
        totals = self.category_totals()
        if totals:
            category, amount = max(totals.items(), key=lambda item: item[1])
            total = sum(totals.values())
            percent = amount / total * 100 if total else 0
        else:
            category, amount, percent = "Other", 0, 0

        body = ctk.CTkFrame(card, fg_color=COLORS["orange_soft"], corner_radius=10)
        body.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        ctk.CTkLabel(body, text="☆", font=ctk.CTkFont(size=27), text_color=COLORS["orange"]).pack(side="right", padx=16)
        ctk.CTkLabel(body, text=category, font=ctk.CTkFont(size=12, weight="bold"), text_color=COLORS["text"]).pack(anchor="w", padx=12, pady=(12, 2))
        ctk.CTkLabel(body, text=f"{self.currency(amount)} ({percent:.1f}%)", font=ctk.CTkFont(size=10), text_color=COLORS["orange"]).pack(anchor="w", padx=12)

    # ========================================================
    # SETTINGS PAGE
    # ========================================================

    def create_settings_page(self):
        self.build_standard_header(
            "⚙",
            "Settings",
            "Customize your experience.",
            COLORS["blue"],
        )

        page = self.content
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(0, weight=2)
        page.grid_rowconfigure(1, weight=1)

        categories_card = ctk.CTkFrame(
            page,
            fg_color=COLORS["card"],
            corner_radius=10,
            border_width=1,
            border_color=COLORS["border"],
        )
        categories_card.grid(row=0, column=0, sticky="nsew", pady=(0, 8))

        ctk.CTkLabel(categories_card, text="Expense Categories", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLORS["text"]).pack(anchor="w", padx=12, pady=(10, 2))
        ctk.CTkLabel(categories_card, text="Manage your categories", font=ctk.CTkFont(size=10), text_color=COLORS["muted"]).pack(anchor="w", padx=12)

        body = ctk.CTkFrame(categories_card, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=12, pady=8)
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=1)

        categories = list(self.categories)
        half = (len(categories) + 1) // 2
        columns = [categories[:half], categories[half:]]
        for col, values in enumerate(columns):
            for row, category in enumerate(values):
                item = ctk.CTkFrame(body, fg_color="transparent")
                item.grid(row=row, column=col, sticky="w", padx=4, pady=4)
                color = CATEGORY_COLORS.get(category, COLORS["blue"])
                dot = tk.Canvas(item, width=14, height=14, highlightthickness=0, bg=COLORS["card"])
                dot.create_oval(3, 3, 11, 11, fill=color, outline=color)
                dot.pack(side="left")
                ctk.CTkLabel(
                    item,
                    text=category,
                    font=ctk.CTkFont(
                        family="Segoe UI",
                        size=13
                    ),
                    text_color=COLORS["text"]
                ).pack(
                    side="left",
                    padx=7
                )
                
        ctk.CTkButton(
            categories_card,
            text="＋ Add Category",
            width=125,
            height=34,
            corner_radius=8,
            fg_color=COLORS["card"],
            hover_color=COLORS["blue_soft"],
            border_width=1,
            border_color=COLORS["blue"],
            text_color=COLORS["blue"],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=12,
                weight="bold"
            ),
            command=self.add_category_dialog,
        ).pack(
            anchor="w",
            padx=12,
            pady=(0, 12)
        )

        export_card = ctk.CTkFrame(
            page,
            fg_color=COLORS["card"],
            corner_radius=10,
            border_width=1,
            border_color=COLORS["border"],
        )
        export_card.grid(row=1, column=0, sticky="nsew")

        ctk.CTkLabel(export_card, text="Backup & Export", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLORS["text"]).pack(anchor="w", padx=12, pady=(10, 2))
        ctk.CTkLabel(export_card, text="Save your data or export it for backup", font=ctk.CTkFont(size=10), text_color=COLORS["muted"]).pack(anchor="w", padx=12)

        buttons = ctk.CTkFrame(export_card, fg_color="transparent")
        buttons.pack(fill="x", padx=12, pady=10)
        buttons.grid_columnconfigure(0, weight=1)
        buttons.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            buttons,
            text="Export to JSON",
            height=34,
            corner_radius=8,
            fg_color=COLORS["blue"],
            hover_color=COLORS["blue_dark"],
            text_color="#FFFFFF",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=12,
                weight="bold"
            ),
            command=self.export_json,
        ).grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 5)
        )

        ctk.CTkButton(
            buttons,
            text="Export to CSV",
            height=34,
            corner_radius=8,
            fg_color=COLORS["blue"],
            hover_color=COLORS["blue_dark"],
            text_color="#FFFFFF",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=12,
                weight="bold"
            ),
            command=self.export_csv,
        ).grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(5, 0)
        )


    def create_about_page(self):

        self.build_standard_header(
            "ℹ",
            "About",
            "Learn more about Student Expense Tracker.",
            COLORS["blue"],
        )

        page = self.content

        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(0, weight=1)

        # Main container
        container = ctk.CTkScrollableFrame(
            page,
            fg_color="transparent",
            corner_radius=0,
        )

        container.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        container.grid_columnconfigure(0, weight=1)

        # -------------------------------------------------
        # APP INTRO
        # -------------------------------------------------

        intro_card = ctk.CTkFrame(
            container,
            fg_color=COLORS["card"],
            corner_radius=14,
            border_width=1,
            border_color=COLORS["border"],
        )

        intro_card.grid(
            row=0,
            column=0,
            sticky="ew",
            pady=(0, 12)
        )

        ctk.CTkLabel(
            intro_card,
            text="💰",
            font=ctk.CTkFont(size=42),
        ).pack(
            pady=(24, 5)
        )

        ctk.CTkLabel(
            intro_card,
            text="Student Expense Tracker",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=24,
                weight="bold"
            ),
            text_color=COLORS["text"],
        ).pack(
            pady=(0, 4)
        )

        ctk.CTkLabel(
            intro_card,
            text="Version 2.0.0",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=12
            ),
            text_color=COLORS["muted"],
        ).pack(
            pady=(0, 16)
        )

        ctk.CTkLabel(
            intro_card,
            text=(
                "A simple and modern expense management application "
                "designed to help students track spending, manage "
                "budgets, and understand their financial habits."
            ),
            font=ctk.CTkFont(
                family="Segoe UI",
                size=13
            ),
            text_color=COLORS["text"],
            justify="center",
            wraplength=700,
        ).pack(
            padx=40,
            pady=(0, 25)
        )

        # -------------------------------------------------
        # KEY FEATURES
        # -------------------------------------------------

        features_card = ctk.CTkFrame(
            container,
            fg_color=COLORS["card"],
            corner_radius=14,
            border_width=1,
            border_color=COLORS["border"],
        )

        features_card.grid(
            row=1,
            column=0,
            sticky="ew",
            pady=(0, 12)
        )

        ctk.CTkLabel(
            features_card,
            text="Key Features",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=16,
                weight="bold"
            ),
            text_color=COLORS["text"],
        ).pack(
            anchor="w",
            padx=22,
            pady=(18, 10)
        )

        features = [
            "Track and manage daily expenses",
            "Set daily, weekly, and monthly budgets",
            "View spending trends and reports",
            "Search, filter, and sort expenses",
            "Export data to JSON and CSV",
            "Create custom expense categories",
        ]

        for feature in features:

            ctk.CTkLabel(
                features_card,
                text=f"✓  {feature}",
                font=ctk.CTkFont(
                    family="Segoe UI",
                    size=13
                ),
                text_color=COLORS["text"],
            ).pack(
                anchor="w",
                padx=22,
                pady=3
            )

        ctk.CTkFrame(
            features_card,
            height=12,
            fg_color="transparent"
        ).pack()

        # -------------------------------------------------
        # DEVELOPER
        # -------------------------------------------------

        developer_card = ctk.CTkFrame(
            container,
            fg_color=COLORS["card"],
            corner_radius=14,
            border_width=1,
            border_color=COLORS["border"],
        )

        developer_card.grid(
            row=2,
            column=0,
            sticky="ew",
            pady=(0, 12)
        )

        ctk.CTkLabel(
            developer_card,
            text="Created by",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=12
            ),
            text_color=COLORS["muted"],
        ).pack(
            pady=(18, 2)
        )

        ctk.CTkLabel(
            developer_card,
            text="Tosin Yusuf",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=20,
                weight="bold"
            ),
            text_color=COLORS["text"],
        ).pack()

        ctk.CTkLabel(
            developer_card,
            text="Student Developer",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=12
            ),
            text_color=COLORS["blue"],
        ).pack(
            pady=(2, 14)
        )

        # Social links
        social_frame = ctk.CTkFrame(
            developer_card,
            fg_color="transparent"
        )

        social_frame.pack(
            padx=20,
            pady=(0, 20)
        )

        social_frame.grid_columnconfigure(
            0,
            weight=1
        )
        social_frame.grid_columnconfigure(
            1,
            weight=1
        )
        social_frame.grid_columnconfigure(
            2,
            weight=1
        )

        def open_link(url):

            import webbrowser

            webbrowser.open(url)

        # Replace these placeholder URLs with your actual profiles
        social_links = [
            (
                "GitHub",
                "https://github.com/tosinlabs"
            ),
            (
                "LinkedIn",
                "https://www.linkedin.com/in/"
            ),
            (
                "Instagram",
                "https://www.instagram.com/toseiyy"
            ),
            (
                "X",
                "https://x.com/imtosinn"
            ),
            (
                "YouTube",
                "https://www.youtube.com/@imtosinn"
            ),
        ]

        for index, (name, url) in enumerate(social_links):

            row = index // 3
            column = index % 3

            ctk.CTkButton(
                social_frame,
                text=name,
                width=120,
                height=34,
                corner_radius=8,
                fg_color=COLORS["blue_soft"],
                hover_color="#D8E8FF",
                text_color=COLORS["blue_dark"],
                font=ctk.CTkFont(
                    family="Segoe UI",
                    size=12,
                    weight="bold"
                ),
                command=lambda link=url: open_link(link),
            ).grid(
                row=row,
                column=column,
                padx=5,
                pady=5
            )

        # -------------------------------------------------
        # OPEN SOURCE
        # -------------------------------------------------

        license_card = ctk.CTkFrame(
            container,
            fg_color=COLORS["field"],
            corner_radius=14,
            border_width=1,
            border_color=COLORS["border"],
        )

        license_card.grid(
            row=3,
            column=0,
            sticky="ew",
            pady=(0, 12)
        )

        ctk.CTkLabel(
            license_card,
            text="Open Source",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=15,
                weight="bold"
            ),
            text_color=COLORS["text"],
        ).pack(
            anchor="w",
            padx=20,
            pady=(16, 4)
        )

        ctk.CTkLabel(
            license_card,
            text=(
                "Student Expense Tracker is an open-source project "
                "released under the MIT License."
            ),
            font=ctk.CTkFont(
                family="Segoe UI",
                size=12
            ),
            text_color=COLORS["muted"],
            wraplength=700,
            justify="left",
        ).pack(
            anchor="w",
            padx=20,
            pady=(0, 16)
        )

        # -------------------------------------------------
        # PRIVACY & DISCLAIMER
        # -------------------------------------------------

        info_card = ctk.CTkFrame(
            container,
            fg_color=COLORS["card"],
            corner_radius=14,
            border_width=1,
            border_color=COLORS["border"],
        )

        info_card.grid(
            row=4,
            column=0,
            sticky="ew",
            pady=(0, 12)
        )

        ctk.CTkLabel(
            info_card,
            text="Privacy & Disclaimer",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=15,
                weight="bold"
            ),
            text_color=COLORS["text"],
        ).pack(
            anchor="w",
            padx=20,
            pady=(16, 6)
        )

        ctk.CTkLabel(
            info_card,
            text=(
                "This application is designed for personal expense "
                "tracking. Your expense data is stored locally by "
                "the application and is not intended to provide "
                "financial advice."
            ),
            font=ctk.CTkFont(
                family="Segoe UI",
                size=12
            ),
            text_color=COLORS["muted"],
            wraplength=700,
            justify="left",
        ).pack(
            anchor="w",
            padx=20,
            pady=(0, 16)
        )

        # -------------------------------------------------
        # BUILT WITH
        # -------------------------------------------------

        built_card = ctk.CTkFrame(
            container,
            fg_color="transparent"
        )

        built_card.grid(
            row=5,
            column=0,
            sticky="ew",
            pady=(4, 20)
        )

        ctk.CTkLabel(
            built_card,
            text="Built with Python • CustomTkinter • Matplotlib",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=12
            ),
            text_color=COLORS["muted"],
        ).pack()

        ctk.CTkLabel(
            built_card,
            text="Student Expense Tracker • Open Source",
            font=ctk.CTkFont(
                family="Segoe UI",
                size=11
            ),
            text_color=COLORS["muted"],
        ).pack(
            pady=(4, 0)
        )


    def add_category_dialog(self):
        dialog = ctk.CTkInputDialog(text="Enter the new category name:", title="Add Category")
        value = dialog.get_input()
        if not value:
            return

        value = value.strip()
        if not value:
            return

        if value.lower() in {category.lower() for category in self.categories}:
            messagebox.showinfo("Add Category", "That category already exists.", parent=self)
            return

        self.categories.append(value)
        self.save_data()
        self.show_page("Settings")

    def export_json(self):
        path = filedialog.asksaveasfilename(
            title="Export to JSON",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
        )
        if not path:
            return

        with open(path, "w", encoding="utf-8") as file:
            json.dump(
                {
                    "categories": self.categories,
                    "budgets": self.budgets,
                    "expenses": [
                        {
                            **expense,
                            "date": expense["date"].isoformat(),
                        }
                        for expense in self.expenses
                    ],
                },
                file,
                indent=4,
            )
        messagebox.showinfo("Export", "Your data was exported to JSON.", parent=self)

    def export_csv(self):
        path = filedialog.asksaveasfilename(
            title="Export to CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
        )
        if not path:
            return

        with open(path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Expense", "Amount", "Category", "Date"])
            for expense in self.expenses:
                writer.writerow([
                    expense["name"],
                    expense["amount"],
                    expense["category"],
                    expense["date"].isoformat(),
                ])
        messagebox.showinfo("Export", "Your expenses were exported to CSV.", parent=self)

    # ========================================================
    # FEEDBACK & SUPPORT PAGE
    # ========================================================

    def create_feedback_page(self):
        self.build_standard_header(
            "📝",
            "Feedback & Support",
            "Tell us what you think and help us make the app better.",
            COLORS["pink"],
        )

        page = self.content
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(0, weight=1)

        card = ctk.CTkScrollableFrame(
            page,
            fg_color=COLORS["card"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"],
        )
        card.grid(row=0, column=0, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)

        # Rating
        self.add_feedback_section_label(
            card,
            0,
            "How would you rate your experience?",
            "Your rating helps us understand how the app is doing.",
        )

        self.feedback_rating = 0
        self.feedback_star_buttons = []

        stars_frame = ctk.CTkFrame(card, fg_color="transparent")
        stars_frame.grid(row=1, column=0, sticky="w", padx=16, pady=(0, 2))

        for rating in range(1, 6):
            star_button = ctk.CTkButton(
                stars_frame,
                text="☆",
                width=42,
                height=42,
                corner_radius=9,
                fg_color=COLORS["pink_soft"],
                hover_color="#FFD8E4",
                text_color=COLORS["pink"],
                font=ctk.CTkFont(size=27),
                command=lambda value=rating: self.set_feedback_rating(value),
            )
            star_button.pack(side="left", padx=(0, 5))
            self.feedback_star_buttons.append(star_button)

        self.feedback_rating_label = ctk.CTkLabel(
            card,
            text="Select a rating",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS["muted"],
        )
        self.feedback_rating_label.grid(row=2, column=0, sticky="w", padx=17, pady=(0, 8))

        # Feedback type
        self.add_feedback_section_label(
            card,
            3,
            "Feedback Type",
            "What would you like to tell us about?",
        )

        self.feedback_type_menu = ctk.CTkOptionMenu(
            card,
            height=36,
            values=[
                "Bug / Problem",
                "Suggestion",
                "Feature Request",
                "UI / Design",
                "Performance",
                "General Feedback",
                "Other",
            ],
            fg_color=COLORS["field"],
            button_color=COLORS["pink"],
            button_hover_color="#D12F5B",
            text_color=COLORS["text"],
            dropdown_fg_color=COLORS["card"],
            dropdown_text_color=COLORS["text"],
        )
        self.feedback_type_menu.grid(row=4, column=0, sticky="ew", padx=16, pady=(0, 8))
        self.feedback_type_menu.set("General Feedback")

        # Title
        self.add_feedback_section_label(
            card,
            5,
            "Title",
            "Give your feedback a short title.",
        )

        self.feedback_title_entry = ctk.CTkEntry(
            card,
            height=36,
            placeholder_text="e.g. The dashboard is easy to use",
            fg_color=COLORS["field"],
            border_color=COLORS["border"],
            text_color=COLORS["text"],
        )
        self.feedback_title_entry.grid(row=6, column=0, sticky="ew", padx=16, pady=(0, 8))

        # Detailed feedback
        self.add_feedback_section_label(
            card,
            7,
            "Detailed Feedback",
            "Tell us more about your experience, issue, or idea.",
        )

        self.feedback_message_text = ctk.CTkTextbox(
            card,
            height=130,
            fg_color=COLORS["field"],
            border_width=1,
            border_color=COLORS["border"],
            text_color=COLORS["text"],
            corner_radius=8,
        )
        self.feedback_message_text.grid(row=8, column=0, sticky="ew", padx=16, pady=(0, 2))
        self.feedback_message_text.bind("<KeyRelease>", self.update_feedback_character_count)

        self.feedback_character_label = ctk.CTkLabel(
            card,
            text="0/1000",
            font=ctk.CTkFont(size=10),
            text_color=COLORS["muted"],
        )
        self.feedback_character_label.grid(row=9, column=0, sticky="e", padx=18, pady=(0, 8))

        # Contact details
        self.add_feedback_section_label(
            card,
            10,
            "Your Details",
            "Add your name and email so feedback can be identified or followed up.",
        )

        self.feedback_name_entry = ctk.CTkEntry(
            card,
            height=36,
            placeholder_text="Your name",
            fg_color=COLORS["field"],
            border_color=COLORS["border"],
            text_color=COLORS["text"],
        )
        self.feedback_name_entry.grid(row=11, column=0, sticky="ew", padx=16, pady=(0, 7))

        self.feedback_email_entry = ctk.CTkEntry(
            card,
            height=36,
            placeholder_text="Your email address",
            fg_color=COLORS["field"],
            border_color=COLORS["border"],
            text_color=COLORS["text"],
        )
        self.feedback_email_entry.grid(row=12, column=0, sticky="ew", padx=16, pady=(0, 4))

        ctk.CTkLabel(
            card,
            text="Your email is only used to identify or respond to your feedback.",
            font=ctk.CTkFont(size=10),
            text_color=COLORS["muted"],
        ).grid(row=13, column=0, sticky="w", padx=17, pady=(0, 10))

        # Automatically included app information
        info_card = ctk.CTkFrame(
            card,
            fg_color=COLORS["pink_soft"],
            corner_radius=8,
            border_width=1,
            border_color="#F8C6D5",
        )
        info_card.grid(row=14, column=0, sticky="ew", padx=16, pady=(0, 10))

        ctk.CTkLabel(
            info_card,
            text="App Information",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS["pink"],
        ).pack(anchor="w", padx=12, pady=(8, 2))

        ctk.CTkLabel(
            info_card,
            text="Version 2.0.0  •  Windows  •  Student Expense Tracker",
            font=ctk.CTkFont(size=10),
            text_color=COLORS["text"],
        ).pack(anchor="w", padx=12, pady=(0, 8))

        ctk.CTkButton(
            card,
            text="Submit Feedback",
            height=40,
            corner_radius=8,
            fg_color=COLORS["pink"],
            hover_color="#D12F5B",
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.submit_feedback,
        ).grid(row=15, column=0, sticky="ew", padx=16, pady=(0, 16))

    def add_feedback_section_label(self, parent, row, title, subtitle):
        section = ctk.CTkFrame(parent, fg_color="transparent")
        section.grid(row=row, column=0, sticky="ew", padx=16, pady=(8, 5))

        ctk.CTkLabel(
            section,
            text=title,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["text"],
        ).pack(anchor="w")

        ctk.CTkLabel(
            section,
            text=subtitle,
            font=ctk.CTkFont(size=10),
            text_color=COLORS["muted"],
        ).pack(anchor="w", pady=(1, 0))

    def set_feedback_rating(self, rating):
        self.feedback_rating = rating
        labels = {
            1: "1 / 5 — Very Poor",
            2: "2 / 5 — Poor",
            3: "3 / 5 — Okay",
            4: "4 / 5 — Good",
            5: "5 / 5 — Excellent",
        }

        for index, button in enumerate(self.feedback_star_buttons, start=1):
            if index <= rating:
                button.configure(text="★", fg_color=COLORS["pink"], text_color="#FFFFFF")
            else:
                button.configure(text="☆", fg_color=COLORS["pink_soft"], text_color=COLORS["pink"])

        self.feedback_rating_label.configure(
            text=labels[rating],
            text_color=COLORS["pink"],
        )

    def update_feedback_character_count(self, _event=None):
        text = self.feedback_message_text.get("1.0", "end-1c")
        count = len(text)

        if count > 1000:
            self.feedback_message_text.delete("1.0 + 1000 chars", "end")
            count = 1000

        self.feedback_character_label.configure(text=f"{count}/1000")

    @staticmethod
    def is_valid_email(email):
        return (
            email.count("@") == 1
            and " " not in email
            and "." in email.split("@", 1)[1]
            and email.split("@", 1)[1].strip(".") != ""
        )

    def submit_feedback(self):
        rating = self.feedback_rating
        feedback_type = self.feedback_type_menu.get().strip()
        title = self.feedback_title_entry.get().strip()
        message = self.feedback_message_text.get("1.0", "end-1c").strip()
        name = self.feedback_name_entry.get().strip()
        email = self.feedback_email_entry.get().strip()

        if rating == 0:
            messagebox.showerror(
                "Feedback",
                "Please select a rating from 1 to 5 stars.",
                parent=self,
            )
            return

        if not title:
            messagebox.showerror(
                "Feedback",
                "Please enter a title for your feedback.",
                parent=self,
            )
            self.feedback_title_entry.focus()
            return

        if not message:
            messagebox.showerror(
                "Feedback",
                "Please enter your detailed feedback.",
                parent=self,
            )
            self.feedback_message_text.focus()
            return

        if not name:
            messagebox.showerror(
                "Feedback",
                "Please enter your name.",
                parent=self,
            )
            self.feedback_name_entry.focus()
            return

        if not self.is_valid_email(email):
            messagebox.showerror(
                "Feedback",
                "Please enter a valid email address.",
                parent=self,
            )
            self.feedback_email_entry.focus()
            return

        feedback_item = {
            "rating": rating,
            "type": feedback_type,
            "title": title,
            "message": message,
            "name": name,
            "email": email,
            "app_version": "2.0.0",
            "platform": "Windows",
            "product": "Student Expense Tracker",
            "submitted_at": datetime.now().isoformat(timespec="seconds"),
        }

        feedback_items = []
        if self.feedback_file.exists():
            try:
                with self.feedback_file.open("r", encoding="utf-8") as file:
                    existing = json.load(file)
                    if isinstance(existing, list):
                        feedback_items = existing
            except (OSError, json.JSONDecodeError):
                feedback_items = []

        feedback_items.append(feedback_item)

        try:
            with self.feedback_file.open("w", encoding="utf-8") as file:
                json.dump(feedback_items, file, indent=4, ensure_ascii=False)
        except OSError as error:
            messagebox.showerror(
                "Feedback",
                f"Could not save your feedback.\n\n{error}",
                parent=self,
            )
            return

        messagebox.showinfo(
            "Feedback Submitted",
            "Thank you for your feedback!\n\nYour response has been saved successfully.",
            parent=self,
        )
        self.clear_feedback_form()

    def clear_feedback_form(self):
        self.feedback_rating = 0

        for button in self.feedback_star_buttons:
            button.configure(
                text="☆",
                fg_color=COLORS["pink_soft"],
                text_color=COLORS["pink"],
            )

        self.feedback_rating_label.configure(
            text="Select a rating",
            text_color=COLORS["muted"],
        )
        self.feedback_type_menu.set("General Feedback")
        self.feedback_title_entry.delete(0, "end")
        self.feedback_message_text.delete("1.0", "end")
        self.feedback_name_entry.delete(0, "end")
        self.feedback_email_entry.delete(0, "end")
        self.feedback_character_label.configure(text="0/1000")

    # ========================================================
    # HELPERS
    # ========================================================

    def add_form_label(self, parent, text):
        ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS["text"],
        ).pack(anchor="w", pady=(10, 4))

    def find_expense(self, expense_id):
        for expense in self.expenses:
            if expense["id"] == expense_id:
                return expense
        return None

    def total_spending(self):
        return sum(expense["amount"] for expense in self.expenses)

    def calculate_period_spending(self, period):
        today = datetime.now().date()

        if period == "Daily":
            start = today
        elif period == "Weekly":
            start = today - timedelta(days=today.weekday())
        else:
            start = today.replace(day=1)

        return sum(
            expense["amount"]
            for expense in self.expenses
            if start <= expense["date"] <= today
        )

    def category_totals(self):
        totals = {}
        for expense in self.expenses:
            totals[expense["category"]] = totals.get(expense["category"], 0) + expense["amount"]
        return totals

    @staticmethod
    def currency(amount, decimals=2):
        return f"₦{amount:,.{decimals}f}"


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    app = ExpenseTracker()
    app.mainloop()