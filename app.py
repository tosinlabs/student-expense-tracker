import csv
import os
from pathlib import Path
import shutil
import sys
import uuid
import requests
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
import tkinter as tk
from pathlib import Path
from datetime import datetime, timedelta
from tkinter import filedialog, messagebox
from PIL import Image

import customtkinter as ctk


# ============================================================
# FILE LOCATIONS (works both as a script and as a built .exe)
# ============================================================

APP_NAME = "StudentExpenseTracker"


def resource_path(relative_path):
    """Path to a bundled file (e.g. assets/...), script or .exe."""
    base = getattr(sys, "_MEIPASS", Path(__file__).parent)
    return Path(base) / relative_path


DATA_DIR = Path(os.getenv("APPDATA", Path.home())) / APP_NAME

try:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
except OSError:
    pass


def data_path(filename):
    """Path to a user data file in the app data folder.

    If an old copy exists next to the app (from before this change),
    it is copied over once so no existing data is lost.
    """
    new_path = DATA_DIR / filename
    old_path = Path(filename)

    if not new_path.exists() and old_path.exists():
        try:
            shutil.copy2(old_path, new_path)
        except OSError:
            pass

    return new_path




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


BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"

TASKBAR_LOGO = ASSETS_DIR / "student tracker 2.png"
SIDEBAR_LOGO = ASSETS_DIR / "logo 2.png"
SPLASH_LOGO = ASSETS_DIR / "logo3.png"


# ============================================================
# APP
# ============================================================

class ExpenseTracker(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.iconbitmap(str(ASSETS_DIR / "student_tracker.ico"))

        self.title("Student Expense Tracker")
        self.geometry("1366x720")
        self.minsize(1100, 700)
        self.configure(fg_color=COLORS["window"])
        self.set_app_icon()

        self.grid_columnconfigure(0, weight=0, minsize=155)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.feedback_file = data_path("student_expense_tracker_feedback.json")
        self.categories = DEFAULT_CATEGORIES.copy()
        self.budgets = {
        }
        self.expenses = []
        self.editing_expense_id = None
        self.current_page = "Dashboard"

        self.load_data()

        self.create_sidebar()
        self.create_main_area()
        self.show_page("Dashboard")


    # ========================================================
    # WINDOW ICON
    # ========================================================

    def set_app_icon(self):
        """Load the optional custom window icon from the assets folder."""
        ico_path = resource_path("assets/app_icon.ico")
        png_path = resource_path("assets/app_icon.png")

        try:
            if ico_path.is_file():
                self.iconbitmap(str(ico_path))
            elif png_path.is_file():
                self._app_icon_image = tk.PhotoImage(file=str(png_path))
                self.iconphoto(True, self._app_icon_image)
        except (tk.TclError, OSError) as error:
            print(f"App icon could not be loaded: {error}")


    # ========================================================
    # DATA
    # ========================================================

    def load_data(self):

        # -----------------------------
        # LOAD EXPENSES
        # -----------------------------

        self.expenses = []

        expenses_file = data_path("expenses.json")

        if expenses_file.exists():
            try:
                with expenses_file.open(
                    "r",
                    encoding="utf-8"
                ) as file:
                    data = json.load(file)

                if isinstance(data, list):
                    for item in data:
                        self.expenses.append(
                            {
                                "id": item.get(
                                    "id",
                                    self.new_id()
                                ),
                                "name": item["name"],
                                "amount": float(
                                    item["amount"]
                                ),
                                "category": item["category"],
                                "date": datetime.strptime(
                                    item["date"],
                                    "%Y-%m-%d"
                                ).date(),
                            }
                        )

            except (
                OSError,
                json.JSONDecodeError,
                KeyError,
                TypeError,
                ValueError
            ):
                self.expenses = []

        # -----------------------------
        # LOAD BUDGETS
        # -----------------------------

        self.budgets = {
        }

        budget_file = data_path("budget.json")

        if budget_file.exists():
            try:
                with budget_file.open(
                    "r",
                    encoding="utf-8"
                ) as file:
                    budget_data = json.load(file)

                if isinstance(budget_data, dict):
                    self.budgets = {
                        period: float(amount)
                        for period, amount in budget_data.items()
                    }

            except (
                OSError,
                json.JSONDecodeError,
                TypeError,
                ValueError
            ):
                pass

        # -----------------------------
        # LOAD CUSTOM CATEGORIES
        # -----------------------------
        categories_file = data_path("categories.json")
        if categories_file.exists():
            try:
                with categories_file.open("r", encoding="utf-8") as file:
                    saved_categories = json.load(file)
                if isinstance(saved_categories, list):
                    valid_categories = [
                        item.strip() for item in saved_categories
                        if isinstance(item, str) and item.strip()
                    ]
                    self.categories = list(dict.fromkeys(
                        self.categories + valid_categories
                    ))
            except (OSError, json.JSONDecodeError, TypeError):
                pass

    def save_expenses(self):
        try:
            with data_path("expenses.json").open(
                "w",
                encoding="utf-8"
            ) as file:
                json.dump(
                    [
                        {
                            "id": expense["id"],
                            "name": expense["name"],
                            "amount": expense["amount"],
                            "category": expense["category"],
                            "date": expense["date"].isoformat(),
                        }
                        for expense in self.expenses
                    ],
                    file,
                    indent=4,
                    ensure_ascii=False,
                )
            return True

        except OSError as error:
            messagebox.showerror(
                "Save Error",
                f"Could not save expenses.\n\n{error}",
                parent=self
            )
            return False


    def save_categories_to_file(self):
        try:
            with data_path("categories.json").open("w", encoding="utf-8") as file:
                json.dump(self.categories, file, indent=4, ensure_ascii=False)
            return True
        except OSError as error:
            messagebox.showerror(
                "Save Error",
                f"Could not save categories.\n\n{error}",
                parent=self
            )
            return False


    def save_data(self):
        expenses_saved = self.save_expenses()
        budgets_saved = self.save_budgets_to_file()
        categories_saved = self.save_categories_to_file()
        return expenses_saved and budgets_saved and categories_saved


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
        return f"exp_{uuid.uuid4().hex}"

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
            light_image=Image.open(resource_path(f"assets/{icon_filename}")),
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
            light_image=Image.open(resource_path("assets/calendar(2).png")),
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
            light_image=Image.open(resource_path(f"assets/{icon_filename}")),
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
    
    
    def create_spending_chart(self, parent):

        """Compact spending-by-category bar chart."""
        
        category_colors = {
            "Food": "#FFA72C",
            "Transport": "#2987F7",
            "Educational": "#7B42DF",
            "Shopping": "#0CA56D",
            "Bills": "#F04475",
            "Gifts": "#E85AAD",
            "Utensils": "#F59E0B",
            "Accessories": "#6366F1",
            "Schools": "#14B8A6",
            "Other": "#6B7280",
        }

        chart_frame = ctk.CTkFrame(
            parent,
            fg_color=COLORS["card"],
            corner_radius=10,
            border_width=1,
            border_color=COLORS["border"],
        )

        chart_frame.pack(
            fill="x",
            padx=12,
            pady=(10, 10),
        )

        # TITLE
        ctk.CTkLabel(
            chart_frame,
            text="Spending by Category",
            font=ctk.CTkFont(
                size=16,
                weight="bold",
            ),
            text_color=COLORS["text"],
        ).pack(
            anchor="w",
            padx=14,
            pady=(12, 4),
        )

        # GROUP EXPENSES BY CATEGORY
        category_totals = {}

        for expense in self.expenses:
            category = expense["category"]
            category_totals[category] = (
                category_totals.get(category, 0)
                + expense["amount"]
            )

        # NO DATA
        if not category_totals:
            ctk.CTkLabel(
                chart_frame,
                text="No spending data available yet.",
                font=ctk.CTkFont(size=11),
                text_color=COLORS["muted"],
            ).pack(
                pady=25,
            )
            return

        # SORT FROM HIGHEST TO LOWEST
        sorted_categories = sorted(
            category_totals.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        categories = [
            item[0]
            for item in sorted_categories
        ]

        amounts = [
            item[1]
            for item in sorted_categories
        ]

        # CREATE MATPLOTLIB FIGURE
        figure = Figure(
            figsize=(5.5, 1.8),
            dpi=100,
        )

        axis = figure.add_subplot(111)
        bar_colors = [
            category_colors.get(category, "#6B7280")
            for category in categories
        ]
    
        bars = axis.bar(
            categories,
            amounts,
            color=bar_colors,
        )

        for bar, amount in zip(bars, amounts):
            axis.annotate(
                self.currency(amount),
                (
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height(),
                ),
                ha="center",
                va="bottom",
                fontsize=8,
                fontweight="bold",
                color=COLORS["text"],
                xytext=(0, 4),
                textcoords="offset points",
            )
        axis.set_ylabel("") 

        axis.tick_params(
            axis="x",
            labelsize=8,
            bottom=False,
            labelbottom=True,
        )

        for label in axis.get_xticklabels():
            label.set_fontweight("bold")
            label.set_color(COLORS["muted"])

        axis.tick_params(
            axis="y",
            left=False,
            labelleft=False,
        )

        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)
        axis.spines["left"].set_visible(False)
        axis.spines["bottom"].set_visible(False)

        axis.set_facecolor("none")

        figure.tight_layout(
            pad=1.5,
        )

        # EMBED CHART INTO CUSTOMTKINTER
        canvas = FigureCanvasTkAgg(
            figure,
            master=chart_frame,
        )

        canvas.draw()

        canvas.get_tk_widget().pack(
            fill="x",
            padx=10,
            pady=(0, 10),
        )
        
        
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

        # --------------------------------
        # TITLE
        # --------------------------------

        title_frame = ctk.CTkFrame(
            table_card,
            fg_color="transparent",
        )

        title_frame.pack(
            fill="x",
            padx=14,
            pady=(12, 8),
        )

        ctk.CTkLabel(
            title_frame,
            text="Recent Expenses",
            font=ctk.CTkFont(
                size=16,
                weight="bold",
            ),
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
            font=ctk.CTkFont(
                size=10,
                weight="bold",
            ),
            command=lambda: self.show_page("View Expenses"),
        ).pack(side="right")

        # --------------------------------
        # TABLE
        # --------------------------------

        table = ctk.CTkFrame(
            table_card,
            fg_color="transparent",
        )

        table.pack(
            fill="both",
            expand=True,
            padx=12,
            pady=(0, 10),
        )

        # Shared column widths
        table.grid_columnconfigure(0, weight=3)
        table.grid_columnconfigure(1, weight=2)
        table.grid_columnconfigure(2, weight=2)
        table.grid_columnconfigure(3, weight=2)

        # --------------------------------
        # HEADER
        # --------------------------------

        header_row = ctk.CTkFrame(
            table,
            fg_color=COLORS["field"],
            height=30,
            corner_radius=6,
        )

        header_row.grid(
            row=0,
            column=0,
            columnspan=4,
            sticky="ew",
            pady=(0, 7),
        )

        # Match the main table columns
        header_row.grid_columnconfigure(0, weight=3)
        header_row.grid_columnconfigure(1, weight=2)
        header_row.grid_columnconfigure(2, weight=2)
        header_row.grid_columnconfigure(3, weight=2)

        headers = [
            ("Expense", 0, "w"),
            ("Amount", 1, "e"),
            ("Category", 2, "e"),
            ("Date", 3, "e"),
        ]

        for text, column, anchor in headers:

            ctk.CTkLabel(
                header_row,
                text=text,
                font=ctk.CTkFont(
                    size=10,
                    weight="bold",
                ),
                text_color=COLORS["muted"],
                anchor=anchor,
            ).grid(
                row=0,
                column=column,
                sticky="ew",
                padx=9,
                pady=5,
            )

        # --------------------------------
        # RECENT EXPENSES
        # --------------------------------

        recent_items = sorted(
            self.expenses,
            key=lambda expense: expense["date"],
            reverse=True,
        )[:4]

        if not recent_items:

            ctk.CTkLabel(
                table,
                text="No expenses recorded yet.",
                font=ctk.CTkFont(size=12),
                text_color=COLORS["muted"],
            ).grid(
                row=1,
                column=0,
                columnspan=4,
                pady=20,
            )

            return

        # --------------------------------
        # CATEGORY COLORS
        # --------------------------------

        category_colors = {
            "Food": "#FFA72C",
            "Transport": "#2987F7",
            "Educational": "#7B42DF",
            "Shopping": "#0CA56D",
            "Bills": "#F04475",
            "Gifts": "#E85AAD",
            "Utensils": "#F59E0B",
            "Accessories": "#6366F1",
            "Schools": "#14B8A6",
            "Other": "#6B7280",
        }

        # --------------------------------
        # EXPENSE ROWS
        # --------------------------------

        for index, exp in enumerate(recent_items):

            row_number = index + 1

            # Alternate row background
            row_background = (
                COLORS["field"]
                if index % 2 == 0
                else "transparent"
            )

            # Expense name frame
            name_frame = ctk.CTkFrame(
                table,
                fg_color=row_background,
                corner_radius=8,
            )

            name_frame.grid(
                row=row_number,
                column=0,
                sticky="nsew",
                pady=2,
                padx=(0, 3),
            )

            # Category color
            category_color = category_colors.get(
                exp["category"],
                "#6B7280",
            )

            # Colored dot
            ctk.CTkFrame(
                name_frame,
                width=7,
                height=7,
                corner_radius=4,
                fg_color=category_color,
            ).pack(
                side="left",
                padx=(8, 8),
            )

            # Expense name
            ctk.CTkLabel(
                name_frame,
                text=exp["name"],
                font=ctk.CTkFont(
                    size=11,
                    weight="bold",
                ),
                text_color=COLORS["text"],
                anchor="w",
            ).pack(
                side="left",
            )

            # Amount
            ctk.CTkLabel(
                table,
                text=self.currency(exp["amount"]),
                font=ctk.CTkFont(
                    size=11,
                    weight="bold",
                ),
                text_color=COLORS["text"],
                anchor="e",
                fg_color=row_background,
                corner_radius=8,
            ).grid(
                row=row_number,
                column=1,
                sticky="nsew",
                padx=3,
                pady=2,
            )

            # Category
            ctk.CTkLabel(
                table,
                text=exp["category"],
                font=ctk.CTkFont(
                    size=10,
                ),
                text_color=COLORS["text"],
                anchor="e",
                fg_color=row_background,
                corner_radius=8,
            ).grid(
                row=row_number,
                column=2,
                sticky="nsew",
                padx=3,
                pady=2,
            )

            # Date
            ctk.CTkLabel(
                table,
                text=exp["date"].strftime("%b %d, %Y"),
                font=ctk.CTkFont(
                    size=10,
                    weight="bold",
                ),
                text_color=COLORS["muted"],
                anchor="e",
                fg_color=row_background,
                corner_radius=8, ).grid( row=row_number, column=3, sticky="nsew", padx=(3, 0), pady=2, )
            
        self.create_spending_chart(table_card)
    
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
            font=ctk.CTkFont(size=13),
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
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text"],
            wraplength=250,
            justify="left",
        ).pack(
            anchor="w",
            padx=12,
            pady=(0, 14),
        )

    def get_financial_insight(self):
        """Analyzes expenses to generate dynamic feedback."""
        today = datetime.now().date()
        this_week_spent = self.calculate_period_spending("Weekly")
        weekly_budget = self.budgets.get("Weekly", 0)

        budget_ratio = (this_week_spent / weekly_budget) if weekly_budget > 0 else 0

        week_start = today - timedelta(days=today.weekday())
        week_expenses = [e for e in self.expenses if week_start <= e["date"] <= today]

        cat_totals = {}
        for e in week_expenses:
            cat_totals[e["category"]] = cat_totals.get(e["category"], 0) + e["amount"]

        top_cat = max(cat_totals, key=cat_totals.get) if cat_totals else None
        if weekly_budget <= 0:

            if top_cat:
                top_amount = cat_totals[top_cat]
                category_percentage = (
                (top_amount / this_week_spent) * 100
                if this_week_spent > 0
                else 0
)

                title = f"📊 Primary Expense: {top_cat}"

                text = (
                    f"{top_cat} is your biggest spending category "
                    f"this week at {self.currency(top_amount)}."
                    f" which is {category_percentage:.0f}% of your spending."
                )

                tip = (
                        f"Keep an eye on {top_cat} spending. "
                        f"Small reductions here can make a noticeable difference."
                )

                color = COLORS["blue_dark"]
                bg_color = COLORS["blue_soft"]

            else:
                title = "👋 Start Tracking"

                text = (
                    "Add some expenses and set a weekly budget "
                    "to unlock personalized insights."
                )

                tip = (
                    "A weekly budget makes it easier to understand "
                    "where your money is going."
                )

                color = COLORS["blue_dark"]
                bg_color = COLORS["blue_soft"]

        elif budget_ratio >= 1.0:

            title = "⚠️ Budget Limit Reached"

            text = (
                f"You've spent {self.currency(this_week_spent)}, "
                f"exceeding your weekly budget of "
                f"{self.currency(weekly_budget)}."
            )

            tip = (
                "Try holding off on non-essential expenses "
                "until next week begins."
            )

            color = COLORS["danger"]
            bg_color = COLORS["danger_soft"]

        elif budget_ratio >= 0.75:

            title = "⚡ High Spending Warning"

            text = (
                f"You have used {budget_ratio * 100:.0f}% of your "
                f"weekly budget ({self.currency(this_week_spent)} spent)."
            )

            tip = (
            "Keep non-essential spending low for the rest "
            "of the week to stay within your budget."
            )

            color = COLORS["orange"]
            bg_color = COLORS["orange_soft"]

        elif top_cat:

            top_amount = cat_totals[top_cat]

            title = f"📊 Primary Expense: {top_cat}"

            text = (
                f"{top_cat} is your biggest spending category "
                f"this week at {self.currency(top_amount)}."
            )

            tip = (
                f"Setting a specific spending limit for {top_cat} "
                "can help keep total costs down."
            )

            color = COLORS["blue_dark"]
            bg_color = COLORS["blue_soft"]

        else:

            title = "🎉 Healthy Balance"

            text = (
                f"You've spent {self.currency(this_week_spent)} "
                f"out of {self.currency(weekly_budget)} this week."
            )

            tip = (
                "Great job managing your spending! "
                "Put remaining funds into a savings goal."
            )

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

        # Keep a copy so failed disk writes do not leave unsaved changes in memory.
        previous_expenses = [dict(item) for item in self.expenses]

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

        # Only leave the form after the file has been saved successfully.
        if not self.save_expenses():
            self.expenses = previous_expenses
            return

        self.editing_expense_id = None
        self.show_page("Dashboard")

    # ========================================================
    # VIEW EXPENSES PAGE
    # ========================================================

    def create_view_expenses_page(self):

        self.build_standard_header(
            "🪙",
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
            if period in self.budgets:
                entry.insert(0, str(int(self.budgets[period])))
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

        previous_budgets = self.budgets.copy()
        self.budgets.update(new_values)
        if not self.save_budgets_to_file():
            self.budgets = previous_budgets
            return
        self.show_page("View Budget")



    def save_budgets_to_file(self):
        try:
            with data_path("budget.json").open(
                "w",
                encoding="utf-8"
            ) as file:
                json.dump(
                    self.budgets,
                    file,
                    indent=4,
                    ensure_ascii=False
                )
            return True

        except OSError as error:
            messagebox.showerror(
                "Save Error",
                f"Could not save budgets.\n\n{error}",
                parent=self
            )
            return False


    # ========================================================
    # VIEW BUDGET PAGE
    # ========================================================

    def create_view_budget_page(self):

        self.build_standard_header(
            "🪙",
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
                light_image=Image.open(resource_path(icon)),
                dark_image=Image.open(resource_path(icon)),
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
            "📊",
            "Reports",
            "Understand your spending habits and trends.",
            COLORS["blue"],
        )

        # Scrollable container: each card keeps the height its content
        # needs instead of being squeezed into 1/3 of the window.
        page = ctk.CTkScrollableFrame(
            self.content,
            fg_color="transparent",
            corner_radius=0,
        )

        page.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

        # Layout
        page.grid_columnconfigure(0, weight=1)
        page.grid_columnconfigure(1, weight=1)

        # TOP ROW
        summary_card = self.create_report_card(
            page,
            "Spending Summary",
            0,
            0,
        )

        self.fill_spending_summary(summary_card)

        category_card = self.create_report_card(
            page,
            "Spending by Category",
            0,
            1,
        )

        self.fill_category_report(category_card)

        # MIDDLE ROW: MONTHLY TREND
        trend_card = self.create_report_card(
            page,
            "Monthly Spending Trends",
            1,
            0,
            colspan=2,
            action_text="Export CSV",
            action_command=self.export_report_csv,
        )

        self.fill_monthly_trend_chart(trend_card)

        # BOTTOM ROW
        activity_card = self.create_report_card(
            page,
            "Expense Activity",
            2,
            0,
        )

        self.fill_expense_activity(activity_card)

        highest_card = self.create_report_card(
            page,
            "Highest Spending Category",
            2,
            1,
        )

        self.fill_highest_category(highest_card)


    def create_report_card(
        self,
        parent,
        title,
        row,
        column,
        rowspan=1,
        colspan=1,
        action_text=None,
        action_command=None,
    ):

        """Creates a consistent report card with a title and content area."""

        card = ctk.CTkFrame(
            parent,
            fg_color=COLORS["card"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"],
        )

        # Spacing between cards
        if colspan > 1:
            horizontal_padding = (0, 0)
        elif column == 0:
            horizontal_padding = (0, 8)
        else:
            horizontal_padding = (8, 0)

        vertical_padding = (0, 8) if row < 2 else (0, 0)

        card.grid(
            row=row,
            column=column,
            rowspan=rowspan,
            columnspan=colspan,
            sticky="nsew",
            padx=horizontal_padding,
            pady=vertical_padding,
        )

        # Card heading
        heading = ctk.CTkFrame(
            card,
            fg_color="transparent",
        )

        heading.pack(
            fill="x",
            padx=14,
            pady=(12, 9),
        )

        ctk.CTkLabel(
            heading,
            text=title,
            font=ctk.CTkFont(
                size=14,
                weight="bold",
            ),
            text_color=COLORS["text"],
        ).pack(side="left")

        # Optional header action button
        if action_text and action_command:

            ctk.CTkButton(
                heading,
                text=action_text,
                width=90,
                height=28,
                corner_radius=7,
                fg_color=COLORS["blue"],
                hover_color=COLORS["blue_dark"],
                text_color="#FFFFFF",
                font=ctk.CTkFont(
                    size=10,
                    weight="bold",
                ),
                command=action_command,
            ).pack(side="right")

        # Divider below heading
        ctk.CTkFrame(
            card,
            height=1,
            fg_color=COLORS["border"],
        ).pack(
            fill="x",
            padx=14,
        )

        # Content area
        body = ctk.CTkFrame(
            card,
            fg_color="transparent",
        )

        body.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=(6, 10),
        )

        return body


    # ========================================================
    # SPENDING SUMMARY
    # ========================================================

    def fill_spending_summary(self, card):

        """Displays four compact spending summary tiles."""

        summary_items = [
            (
                "TODAY",
                self.calculate_period_spending("Daily"),
                "Today's expenses",
                "#078B5A",
            ),
            (
                "THIS WEEK",
                self.calculate_period_spending("Weekly"),
                "Current week",
                "#1764B4",
            ),
            (
                "THIS MONTH",
                self.calculate_period_spending("Monthly"),
                "Current month",
                "#6336BA",
            ),
            (
                "TOTAL SPENDING",
                self.total_spending(),
                "All recorded expenses",
                "#D12F5B",
            ),
        ]

        card.grid_columnconfigure(0, weight=1)
        card.grid_columnconfigure(1, weight=1)

        card.grid_rowconfigure(0, weight=1)
        card.grid_rowconfigure(1, weight=1)

        for index, item in enumerate(summary_items):

            label, amount, subtitle, accent = item

            tile = ctk.CTkFrame(
                card,
                fg_color=COLORS["field"],
                corner_radius=10,
                border_width=1,
                border_color=COLORS["border"],
            )

            tile.grid(
                row=index // 2,
                column=index % 2,
                sticky="nsew",
                padx=4,
                pady=4,
            )

            # Coloured accent bar
            ctk.CTkFrame(
                tile,
                width=4,
                corner_radius=3,
                fg_color=accent,
            ).pack(
                side="left",
                fill="y",
                padx=(9, 9),
                pady=10,
            )

            text_frame = ctk.CTkFrame(
                tile,
                fg_color="transparent",
            )

            text_frame.pack(
                side="left",
                fill="both",
                expand=True,
                padx=(0, 5),
                pady=7,
            )

            ctk.CTkLabel(
                text_frame,
                text=label,
                font=ctk.CTkFont(
                    size=9,
                    weight="bold",
                ),
                text_color=COLORS["muted"],
            ).pack(anchor="w")

            ctk.CTkLabel(
                text_frame,
                text=self.currency(amount),
                font=ctk.CTkFont(
                    size=16,
                    weight="bold",
                ),
                text_color=accent,
            ).pack(
                anchor="w",
                pady=(3, 1),
            )

            ctk.CTkLabel(
                text_frame,
                text=subtitle,
                font=ctk.CTkFont(size=9),
                text_color=COLORS["muted"],
            ).pack(anchor="w")


    # ========================================================
    # SPENDING BY CATEGORY
    # ========================================================

    def fill_category_report(self, card):

        """Creates a category donut chart and a matching legend."""

        totals = {
            category: amount
            for category, amount in self.category_totals().items()
            if amount > 0
        }

        if not totals:

            ctk.CTkLabel(
                card,
                text="No category data yet.\n\nAdd an expense to see your breakdown.",
                font=ctk.CTkFont(size=12),
                text_color=COLORS["muted"],
                justify="center",
            ).pack(
                expand=True,
                pady=20,
            )

            return

        sorted_totals = sorted(
            totals.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        labels = [
            category
            for category, amount in sorted_totals
        ]

        values = [
            amount
            for category, amount in sorted_totals
        ]

        palette = [
            CATEGORY_COLORS.get(category, "#9AA8B6")
            for category in labels
        ]

        total = sum(values)

        chart_frame = ctk.CTkFrame(
            card,
            fg_color="transparent",
        )

        chart_frame.pack(
            fill="both",
            expand=True,
        )

        chart_frame.grid_columnconfigure(0, weight=1)
        chart_frame.grid_columnconfigure(1, weight=1)
        chart_frame.grid_rowconfigure(0, weight=1)

        # Donut chart
        figure = Figure(
            figsize=(2.3, 1.65),
            dpi=100,
        )

        figure.patch.set_facecolor(COLORS["card"])

        axis = figure.add_subplot(111)

        axis.set_facecolor(COLORS["card"])

        axis.pie(
            values,
            startangle=90,
            counterclock=False,
            colors=palette,
            wedgeprops={
                "width": 0.38,
                "edgecolor": COLORS["card"],
                "linewidth": 2,
            },
        )

        center_amount = self.currency(
            total,
            decimals=0,
        ).replace(".00", "")

        axis.text(
            0,
            0.06,
            center_amount,
            ha="center",
            va="center",
            fontsize=11,
            fontweight="bold",
            color=COLORS["text"],
        )

        axis.text(
            0,
            -0.15,
            "TOTAL",
            ha="center",
            va="center",
            fontsize=8,
            color=COLORS["muted"],
        )

        axis.set_aspect("equal")
        axis.axis("off")

        figure.tight_layout(pad=0.2)

        canvas = FigureCanvasTkAgg(
            figure,
            master=chart_frame,
        )

        canvas.draw()

        chart_widget = canvas.get_tk_widget()

        chart_widget.configure(
            highlightthickness=0,
        )

        chart_widget.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 4),
            pady=2,
        )

        # Scrollable category legend
        legend = ctk.CTkScrollableFrame(
            chart_frame,
            fg_color="transparent",
            corner_radius=0,
        )

        legend.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(4, 0),
            pady=2,
        )

        for category, amount in sorted_totals:

            category_color = CATEGORY_COLORS.get(
                category,
                "#9AA8B6",
            )

            percentage = (
                amount / total * 100
                if total > 0
                else 0
            )

            row = ctk.CTkFrame(
                legend,
                fg_color="transparent",
            )

            row.pack(
                fill="x",
                pady=4,
            )

            # Category colour indicator
            ctk.CTkFrame(
                row,
                width=8,
                height=8,
                corner_radius=4,
                fg_color=category_color,
            ).pack(
                side="left",
                padx=(0, 7),
            )

            details = ctk.CTkFrame(
                row,
                fg_color="transparent",
            )

            details.pack(
                side="left",
                fill="x",
                expand=True,
            )

            ctk.CTkLabel(
                details,
                text=category,
                font=ctk.CTkFont(
                    size=10,
                    weight="bold",
                ),
                text_color=COLORS["text"],
                anchor="w",
            ).pack(anchor="w")

            ctk.CTkLabel(
                details,
                text=self.currency(amount),
                font=ctk.CTkFont(size=9),
                text_color=COLORS["muted"],
                anchor="w",
            ).pack(anchor="w")

            ctk.CTkLabel(
                row,
                text=f"{percentage:.0f}%",
                font=ctk.CTkFont(
                    size=10,
                    weight="bold",
                ),
                text_color=COLORS["muted"],
            ).pack(side="right")


    # ========================================================
    # MONTHLY SPENDING TRENDS
    # ========================================================

    def fill_monthly_trend_chart(self, card):

        """Charts spending for the current month and five previous months."""

        today = datetime.now().date()

        month_labels = []
        monthly_amounts = []

        # Oldest month first, current month last
        for offset in range(5, -1, -1):

            month_index = (
                today.year * 12
                + (today.month - 1)
                - offset
            )

            year = month_index // 12
            month = month_index % 12 + 1

            month_start = datetime(
                year,
                month,
                1,
            ).date()

            if month == 12:
                next_month = datetime(
                    year + 1,
                    1,
                    1,
                ).date()

            else:
                next_month = datetime(
                    year,
                    month + 1,
                    1,
                ).date()

            amount = sum(
                expense["amount"]
                for expense in self.expenses
                if month_start <= expense["date"] < next_month
            )

            month_labels.append(
                month_start.strftime("%b")
            )

            monthly_amounts.append(amount)

        if not any(amount > 0 for amount in monthly_amounts):

            ctk.CTkLabel(
                card,
                text=(
                    "Your spending trend will appear here "
                    "after you record expenses in the last six months."
                ),
                font=ctk.CTkFont(size=12),
                text_color=COLORS["muted"],
                wraplength=500,
                justify="center",
            ).pack(
                expand=True,
                pady=20,
            )

            return

        figure = Figure(
            figsize=(8.5, 2.3),
            dpi=100,
        )

        figure.patch.set_facecolor(COLORS["card"])

        axis = figure.add_subplot(111)

        axis.set_facecolor(COLORS["card"])

        bars = axis.bar(
            month_labels,
            monthly_amounts,
            color=COLORS["blue"],
            width=0.55,
        )

        # Clean dashboard appearance
        for spine in axis.spines.values():
            spine.set_visible(False)

        axis.tick_params(
            axis="y",
            left=False,
            labelleft=False,
        )

        axis.tick_params(
            axis="x",
            bottom=False,
            labelbottom=True,
            labelsize=9,
            length=0,
        )

        for label in axis.get_xticklabels():
            label.set_color(COLORS["muted"])
            label.set_fontweight("bold")

        axis.grid(
            axis="y",
            color=COLORS["border"],
            linewidth=0.7,
        )

        axis.set_axisbelow(True)

        axis.margins(y=0.3)

        # Display each month's amount above its bar
        for bar, amount in zip(bars, monthly_amounts):

            if amount <= 0:
                continue

            axis.annotate(
                self.currency(
                    amount,
                    decimals=0,
                ).replace(".00", ""),
                (
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height(),
                ),
                ha="center",
                va="bottom",
                fontsize=8,
                fontweight="bold",
                color=COLORS["text"],
                xytext=(0, 3),
                textcoords="offset points",
            )

        figure.tight_layout(pad=1)

        canvas = FigureCanvasTkAgg(
            figure,
            master=card,
        )

        canvas.draw()

        canvas.get_tk_widget().pack(
            fill="both",
            expand=True,
            padx=4,
            pady=(0, 2),
        )


    # ========================================================
    # EXPENSE ACTIVITY
    # ========================================================

    def fill_expense_activity(self, card):

        """Displays useful statistics from recorded expenses."""

        if not self.expenses:

            ctk.CTkLabel(
                card,
                text=(
                    "No expenses recorded yet.\n\n"
                    "Your transaction statistics will appear here."
                ),
                font=ctk.CTkFont(size=12),
                text_color=COLORS["muted"],
                justify="center",
            ).pack(
                expand=True,
                pady=20,
            )

            return

        total_count = len(self.expenses)

        total_amount = sum(
            expense["amount"]
            for expense in self.expenses
        )

        average_amount = total_amount / total_count

        largest_expense = max(
            self.expenses,
            key=lambda expense: expense["amount"],
        )

        latest_expense = max(
            self.expenses,
            key=lambda expense: expense["date"],
        )

        activity_items = [
            (
                "Total Transactions",
                f"{total_count:,}",
                "Recorded expenses",
                COLORS["blue"],
            ),
            (
                "Average Expense",
                self.currency(average_amount),
                "Per transaction",
                COLORS["purple"],
            ),
            (
                "Largest Expense",
                self.currency(largest_expense["amount"]),
                largest_expense["name"],
                COLORS["orange"],
            ),
            (
                "Latest Activity",
                latest_expense["date"].strftime("%b %d, %Y"),
                latest_expense["name"],
                COLORS["green"],
            ),
        ]

        card.grid_columnconfigure(0, weight=1)
        card.grid_columnconfigure(1, weight=1)

        card.grid_rowconfigure(0, weight=1)
        card.grid_rowconfigure(1, weight=1)

        for index, item in enumerate(activity_items):

            title, value, subtitle, accent = item

            tile = ctk.CTkFrame(
                card,
                fg_color=COLORS["field"],
                corner_radius=9,
                border_width=1,
                border_color=COLORS["border"],
            )

            tile.grid(
                row=index // 2,
                column=index % 2,
                sticky="nsew",
                padx=4,
                pady=4,
            )

            ctk.CTkLabel(
                tile,
                text=title,
                font=ctk.CTkFont(
                    size=10,
                    weight="bold",
                ),
                text_color=COLORS["muted"],
            ).pack(
                anchor="w",
                padx=9,
                pady=(8, 2),
            )

            ctk.CTkLabel(
                tile,
                text=value,
                font=ctk.CTkFont(
                    size=14,
                    weight="bold",
                ),
                text_color=accent,
                wraplength=190,
                justify="left",
            ).pack(
                anchor="w",
                padx=9,
            )

            ctk.CTkLabel(
                tile,
                text=subtitle,
                font=ctk.CTkFont(size=9),
                text_color=COLORS["muted"],
                wraplength=190,
                justify="left",
            ).pack(
                anchor="w",
                padx=9,
                pady=(2, 8),
            )


    # ========================================================
    # HIGHEST SPENDING CATEGORY
    # ========================================================

    def fill_highest_category(self, card):

        """Highlights the category responsible for the most spending."""

        totals = {
            category: amount
            for category, amount in self.category_totals().items()
            if amount > 0
        }

        if not totals:

            ctk.CTkLabel(
                card,
                text=(
                    "No category data available yet.\n\n"
                    "Record an expense to discover your top category."
                ),
                font=ctk.CTkFont(size=12),
                text_color=COLORS["muted"],
                justify="center",
            ).pack(
                expand=True,
                pady=20,
            )

            return

        category, amount = max(
            totals.items(),
            key=lambda item: item[1],
        )

        overall_total = sum(totals.values())

        percentage = (
            amount / overall_total * 100
            if overall_total > 0
            else 0
        )

        category_color = CATEGORY_COLORS.get(
            category,
            COLORS["orange"],
        )

        # Featured category panel
        highlight = ctk.CTkFrame(
            card,
            fg_color=COLORS["orange_soft"],
            corner_radius=10,
        )

        highlight.pack(
            fill="x",
            padx=3,
            pady=(3, 12),
        )

        ctk.CTkLabel(
            highlight,
            text="HIGHEST-SPENDING CATEGORY",
            font=ctk.CTkFont(
                size=9,
                weight="bold",
            ),
            text_color=COLORS["orange"],
        ).pack(
            anchor="w",
            padx=12,
            pady=(10, 3),
        )

        details = ctk.CTkFrame(
            highlight,
            fg_color="transparent",
        )

        details.pack(
            fill="x",
            padx=12,
            pady=(0, 10),
        )

        ctk.CTkLabel(
            details,
            text=category,
            font=ctk.CTkFont(
                size=17,
                weight="bold",
            ),
            text_color=COLORS["text"],
        ).pack(side="left")

        ctk.CTkLabel(
            details,
            text=self.currency(amount),
            font=ctk.CTkFont(
                size=13,
                weight="bold",
            ),
            text_color=category_color,
        ).pack(side="right")

        # Percentage of total spending
        ctk.CTkLabel(
            card,
            text=f"{percentage:.1f}% of total recorded spending",
            font=ctk.CTkFont(
                size=11,
                weight="bold",
            ),
            text_color=COLORS["text"],
        ).pack(
            anchor="w",
            padx=5,
            pady=(0, 7),
        )

        progress = ctk.CTkProgressBar(
            card,
            height=10,
            corner_radius=5,
            fg_color=COLORS["border"],
            progress_color=category_color,
        )

        progress.pack(
            fill="x",
            padx=5,
            pady=(0, 10),
        )

        progress.set(
            max(0, min(percentage / 100, 1))
        )

        ctk.CTkLabel(
            card,
            text=(
                f"{category} accounts for "
                f"{self.currency(amount)} across your recorded expenses."
            ),
            font=ctk.CTkFont(size=10),
            text_color=COLORS["muted"],
            wraplength=320,
            justify="left",
        ).pack(
            anchor="w",
            padx=5,
        )


    # ========================================================
    # EXPORT REPORT TO CSV
    # ========================================================

    def export_report_csv(self):

        """Exports all recorded expenses to a CSV file."""

        if not self.expenses:

            messagebox.showinfo(
                "Export Report",
                "There are no expenses to export yet.",
                parent=self,
            )

            return

        destination = filedialog.asksaveasfilename(
            parent=self,
            title="Export Expense Report",
            defaultextension=".csv",
            initialfile=(
                f"student_expense_report_"
                f"{datetime.now():%Y-%m-%d}.csv"
            ),
            filetypes=[
                ("CSV files", "*.csv"),
            ],
        )

        if not destination:
            return

        try:

            with open(
                destination,
                "w",
                newline="",
                encoding="utf-8-sig",
            ) as csv_file:

                writer = csv.writer(csv_file)

                writer.writerow([
                    "Date",
                    "Expense",
                    "Category",
                    "Amount (NGN)",
                ])

                # Latest expenses first
                for expense in sorted(
                    self.expenses,
                    key=lambda item: item["date"],
                    reverse=True,
                ):

                    writer.writerow([
                        expense["date"].strftime("%d/%m/%Y"),
                        expense["name"],
                        expense["category"],
                        expense["amount"],
                    ])

            messagebox.showinfo(
                "Export Successful",
                f"Your expense report was saved to:\n\n{destination}",
                parent=self,
            )

        except (OSError, csv.Error) as error:

            messagebox.showerror(
                "Export Failed",
                f"Could not export your report.\n\n{error}",
                parent=self,
            )

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
        if not self.save_categories_to_file():
            self.categories.pop()
            return
        self.show_page("Settings")

    def export_json(self):
        path = filedialog.asksaveasfilename(
            title="Export to JSON",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
        )
        if not path:
            return

        try:
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
                    ensure_ascii=False,
                )
        except OSError as error:
            messagebox.showerror("Export Error", f"Could not export JSON.\n\n{error}", parent=self)
            return
        messagebox.showinfo("Export", "Your data was exported to JSON.", parent=self)

    def export_csv(self):
        path = filedialog.asksaveasfilename(
            title="Export to CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
        )
        if not path:
            return

        try:
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
        except OSError as error:
            messagebox.showerror("Export Error", f"Could not export CSV.\n\n{error}", parent=self)
            return
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
            height=44,
            corner_radius=8,
            fg_color=COLORS["pink"],
            hover_color="#D12F5B",
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.submit_feedback,
        ).grid(row=15, column=0, sticky="ew", padx=16, pady=(4,20))


    def set_feedback_rating(self, rating):
        self.feedback_rating = rating

        labels = {
            1: "1 / 5 — Very Poor",
            2: "2 / 5 — Poor",
            3: "3 / 5 — Okay",
            4: "4 / 5 — Good",
            5: "5 / 5 — Excellent",
        }

        for index, button in enumerate(
            self.feedback_star_buttons,
            start=1
        ):
            if index <= rating:
                button.configure(
                    text="★",
                    fg_color=COLORS["pink"],
                    text_color="#FFFFFF"
                )
            else:
                button.configure(
                    text="☆",
                    fg_color=COLORS["pink_soft"],
                    text_color=COLORS["pink"]
                )

        self.feedback_rating_label.configure(
            text=labels[rating],
            text_color=COLORS["pink"]
        )


    def update_feedback_character_count(self, _event=None):

        text = self.feedback_message_text.get(
            "1.0",
            "end-1c"
        )

        count = len(text)

        if count > 1000:
            self.feedback_message_text.delete(
                "1.0 + 1000 chars",
                "end"
            )
            count = 1000

        self.feedback_character_label.configure(
            text=f"{count}/1000"
        )


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


    def is_valid_email(self, email):
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

        # ---------------- VALIDATION ----------------

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

        # ---------------- FEEDBACK DATA ----------------

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

        # ---------------- LOCAL BACKUP ----------------

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
                json.dump(
                    feedback_items,
                    file,
                    indent=4,
                    ensure_ascii=False,
                )

        except OSError as error:
            messagebox.showerror(
                "Feedback",
                f"Could not save your feedback.\n\n{error}",
                parent=self,
            )
            return

        # ---------------- SEND TO VERCEL ----------------

        api_url = (
            "https://student-expense-tracker-kohl-ten.vercel.app"
            "/api/send-feedback"
        )

        api_data = {
            "rating": rating,
            "feedback_type": feedback_type,
            "title": title,
            "feedback": message,
            "name": name,
            "email": email,
            "app_version": "2.0.0",
        }

        try:
            response = requests.post(
                api_url,
                json=api_data,
                timeout=15,
            )

            response.raise_for_status()

            result = response.json()

            if not result.get("success"):
                raise Exception("The feedback server did not accept the submission.")

        except requests.RequestException:
            messagebox.showwarning(
                "Feedback Saved",
                "Your feedback was saved on this device, "
                "but we couldn't send it to the feedback server right now.\n\n"
                "Please check your internet connection and try again later.",
                parent=self,
            )

            self.clear_feedback_form()
            return

        except Exception:
            messagebox.showwarning(
                "Feedback Saved",
                "Your feedback was saved on this device, "
                "but we couldn't send it to the feedback server.",
                parent=self,
            )

            self.clear_feedback_form()
            return

        # ---------------- SUCCESS ----------------

        messagebox.showinfo(
            "Feedback Submitted",
            "Thank you for your feedback!\n\n"
            "Your response has been saved and sent successfully.",
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