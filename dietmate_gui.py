# -------------------------------------------------------------
# 🌿 Dietmate – Adaptive Meal Planner (Colorful GUI Version)
# -------------------------------------------------------------
# Features:
# - Profile management
# - Adaptive 7-day meal plan generation
# - Save/load profile & plans
# - Recipe filtering by preference, allergies
# - Shopping list export
# - Calorie visualization chart
# - Modern colorful interface using ttkbootstrap
# -------------------------------------------------------------

import tkinter as tk
from tkinter import messagebox, filedialog
import json, random, os
from datetime import datetime
import matplotlib.pyplot as plt
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# --------------------------- DATA FILES ---------------------------
DATA_DIR = os.path.join(os.path.expanduser("~"), ".dietmate")
PROFILE_FILE = os.path.join(DATA_DIR, "profile.json")
PLANS_FILE = os.path.join(DATA_DIR, "plans.json")
RECIPES_FILE = os.path.join(DATA_DIR, "recipes.json")

os.makedirs(DATA_DIR, exist_ok=True)

# --------------------------- SAMPLE RECIPES ---------------------------
SAMPLE_RECIPES = [
    {"name": "Oatmeal Bowl", "meal": "Breakfast", "diet": "vegan", "cal": 320, "protein": 8, "carbs": 45, "fat": 9, "ingredients": ["Oats", "Banana", "Almond milk"]},
    {"name": "Grilled Chicken Salad", "meal": "Lunch", "diet": "omnivore", "cal": 420, "protein": 38, "carbs": 18, "fat": 20, "ingredients": ["Chicken", "Lettuce", "Olive oil"]},
    {"name": "Veggie Stir Fry", "meal": "Dinner", "diet": "vegetarian", "cal": 400, "protein": 12, "carbs": 55, "fat": 14, "ingredients": ["Rice", "Bell pepper", "Soy sauce"]},
    {"name": "Smoothie", "meal": "Snack", "diet": "vegan", "cal": 210, "protein": 5, "carbs": 35, "fat": 6, "ingredients": ["Banana", "Spinach", "Oats", "Almond milk"]},
    {"name": "Paneer Wrap", "meal": "Lunch", "diet": "vegetarian", "cal": 460, "protein": 25, "carbs": 40, "fat": 18, "ingredients": ["Paneer", "Tortilla", "Cabbage"]},
    {"name": "Egg Scramble", "meal": "Breakfast", "diet": "omnivore", "cal": 280, "protein": 20, "carbs": 5, "fat": 18, "ingredients": ["Eggs", "Tomato", "Spinach"]},
    {"name": "Tofu Curry", "meal": "Dinner", "diet": "vegan", "cal": 440, "protein": 22, "carbs": 30, "fat": 16, "ingredients": ["Tofu", "Coconut milk", "Curry paste"]}
]

# --------------------------- MAIN CLASS ---------------------------
class DietmateApp(ttk.Window):
    def __init__(self):
        super().__init__(themename="morph")  # 🎨 colorful modern theme
        self.title("🍽️ Dietmate – Adaptive Meal Planner")
        self.geometry("1100x700")
        self.resizable(True, True)

        self.profile = {}
        self.recipes = []
        self.plans = []

        self.create_ui()
        self.load_data()

    # ----------------------- UI SETUP -----------------------
    def create_ui(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)

        # ---------- LEFT PANEL (Profile Section) ----------
        left = ttk.Frame(self, padding=15, bootstyle="info")
        left.grid(row=0, column=0, sticky="nsew")

        ttk.Label(left, text="👤 User Profile", font=("Segoe UI", 14, "bold"), bootstyle="inverse-info").pack(fill=X, pady=5)

        self.name = ttk.Entry(left, width=25)
        self.age = ttk.Entry(left, width=25)
        self.sex = ttk.Combobox(left, values=["Male", "Female", "Other"], width=22)
        self.weight = ttk.Entry(left, width=25)
        self.height = ttk.Entry(left, width=25)
        self.activity = ttk.Combobox(left, values=["Low", "Moderate", "High"], width=22)
        self.goal = ttk.Combobox(left, values=["Lose Weight", "Maintain", "Gain Weight"], width=22)
        self.diet_type = ttk.Combobox(left, values=["omnivore", "vegetarian", "vegan"], width=22)
        self.allergies = ttk.Entry(left, width=25)

        for label, widget in [
            ("Name", self.name), ("Age", self.age), ("Sex", self.sex),
            ("Weight (kg)", self.weight), ("Height (cm)", self.height),
            ("Activity Level", self.activity), ("Goal", self.goal),
            ("Diet Preference", self.diet_type), ("Allergies / Dislikes", self.allergies)
        ]:
            ttk.Label(left, text=label).pack(anchor="w", pady=(8, 0))
            widget.pack(pady=2, fill=X)

        ttk.Button(left, text="💾 Save Profile", bootstyle="success", command=self.save_profile).pack(fill=X, pady=5)
        ttk.Button(left, text="📂 Load Sample Recipes", bootstyle="info", command=self.load_sample_recipes).pack(fill=X)
        ttk.Button(left, text="🧠 Generate 7-day Plan", bootstyle="primary", command=self.generate_plan).pack(fill=X, pady=(5, 0))

        # ---------- RIGHT PANEL (Meal Plan Display) ----------
        right = ttk.Frame(self, padding=15)
        right.grid(row=0, column=1, sticky="nsew")

        ttk.Label(right, text="🍴 Weekly Meal Plan", font=("Segoe UI", 14, "bold"), bootstyle="inverse-primary").pack(fill=X, pady=5)
        self.plan_box = tk.Text(right, wrap="word", height=25, bg="#fdfdfd", font=("Segoe UI", 10))
        self.plan_box.pack(fill=BOTH, expand=True)

        bottom = ttk.Frame(right)
        bottom.pack(fill=X, pady=10)
        ttk.Button(bottom, text="📊 Show Calorie Chart", bootstyle="warning", command=self.show_chart).pack(side=RIGHT, padx=5)
        ttk.Button(bottom, text="🛒 Export Shopping List", bootstyle="danger", command=self.export_shopping_list).pack(side=RIGHT, padx=5)

    # ----------------------- DATA HANDLING -----------------------
    def load_data(self):
        if os.path.exists(PROFILE_FILE):
            with open(PROFILE_FILE, "r") as f:
                self.profile = json.load(f)
            for k, widget in [("name", self.name), ("age", self.age), ("weight", self.weight),
                              ("height", self.height), ("allergies", self.allergies)]:
                if k in self.profile:
                    widget.insert(0, str(self.profile[k]))
            for k, widget in [("sex", self.sex), ("activity", self.activity),
                              ("goal", self.goal), ("diet_type", self.diet_type)]:
                if k in self.profile:
                    widget.set(self.profile[k])
        if os.path.exists(RECIPES_FILE):
            with open(RECIPES_FILE, "r") as f:
                self.recipes = json.load(f)

    def save_profile(self):
        self.profile = {
            "name": self.name.get(),
            "age": self.age.get(),
            "sex": self.sex.get(),
            "weight": self.weight.get(),
            "height": self.height.get(),
            "activity": self.activity.get(),
            "goal": self.goal.get(),
            "diet_type": self.diet_type.get(),
            "allergies": self.allergies.get()
        }
        with open(PROFILE_FILE, "w") as f:
            json.dump(self.profile, f, indent=2)
        messagebox.showinfo("✅ Saved", "Profile saved successfully!")

    def load_sample_recipes(self):
        with open(RECIPES_FILE, "w") as f:
            json.dump(SAMPLE_RECIPES, f, indent=2)
        self.recipes = SAMPLE_RECIPES
        messagebox.showinfo("🍲 Loaded", "Sample recipes loaded successfully!")

    # ----------------------- PLAN GENERATION -----------------------
    def generate_plan(self):
        if not self.profile or not self.recipes:
            messagebox.showwarning("⚠️ Missing Info", "Please save your profile and load recipes first.")
            return

        diet = self.profile.get("diet_type", "omnivore")
        allergies = [a.strip().lower() for a in self.profile.get("allergies", "").split(",") if a.strip()]

        filtered = [r for r in self.recipes if r["diet"] == diet or diet == "omnivore"]
        if allergies:
            filtered = [r for r in filtered if not any(a in (", ".join(r["ingredients"])).lower() for a in allergies)]

        if not filtered:
            messagebox.showerror("❌ No Recipes", "No matching recipes found for your preferences!")
            return

        meals = ["Breakfast", "Lunch", "Snack", "Dinner"]
        plan = {}
        for day in range(1, 8):
            plan[f"Day {day}"] = {}
            for meal in meals:
                choices = [r for r in filtered if r["meal"] == meal]
                plan[f"Day {day}"][meal] = random.choice(choices) if choices else random.choice(filtered)

        self.show_plan(plan)

    # ----------------------- DISPLAY -----------------------
    def show_plan(self, plan):
        self.plan_box.delete(1.0, tk.END)
        for day, meals in plan.items():
            self.plan_box.insert(tk.END, f"🌞 {day}\n", "bold")
            for meal, info in meals.items():
                self.plan_box.insert(tk.END, f"  🍽️ {meal}: {info['name']} ({info['cal']} kcal)\n")
            self.plan_box.insert(tk.END, "\n")
        self.plan_box.tag_config("bold", font=("Segoe UI", 11, "bold"))

        self.current_plan = plan

    # ----------------------- SHOPPING LIST & CHART -----------------------
    def export_shopping_list(self):
        if not hasattr(self, "current_plan"):
            messagebox.showwarning("⚠️ No Plan", "Please generate a meal plan first!")
            return

        items = []
        for day in self.current_plan.values():
            for meal in day.values():
                items.extend(meal["ingredients"])
        items = sorted(set(items))

        file = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if not file:
            return

        with open(file, "w") as f:
            f.write("🛒 Dietmate Shopping List\n------------------------\n")
            for i in items:
                f.write(f"• {i}\n")

        messagebox.showinfo("✅ Exported", f"Shopping list saved to:\n{file}")

    def show_chart(self):
        if not hasattr(self, "current_plan"):
            messagebox.showwarning("⚠️ No Plan", "Please generate a plan first!")
            return

        days = []
        calories = []
        for day, meals in self.current_plan.items():
            total = sum(m["cal"] for m in meals.values())
            days.append(day)
            calories.append(total)

        plt.bar(days, calories)
        plt.xlabel("Days")
        plt.ylabel("Calories")
        plt.title("Weekly Calorie Intake")
        plt.show()


# --------------------------- RUN APP ---------------------------
if __name__ == "__main__":
    app = DietmateApp()
    app.mainloop()
