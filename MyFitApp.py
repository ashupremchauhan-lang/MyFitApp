# ===========================================================
# AI-Based Personalized Fitness and Lifestyle (Advanced Version)
# ===========================================================
# Enhanced with: Real exercise names, diet-specific meal plans, equipment-based logic
# ===========================================================

# !pip install -q gradio

import math, os, json
from datetime import datetime
import joblib

try:
    import gradio as gr
except Exception:
    gr = None
    print("⚠️ Gradio not installed. Install it with: pip install gradio")

# -------------------------
# Helper Functions
# -------------------------
def calc_bmi(weight_kg, height_cm):
    if height_cm <= 0:
        raise ValueError("Height must be > 0")
    height_m = height_cm / 100.0
    return round(weight_kg / (height_m ** 2), 2)

def bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 25:
        return "Healthy"
    elif 25 <= bmi < 30:
        return "Overweight"
    else:
        return "Obese"

# -------------------------
# Main Recommendation Logic
# -------------------------
def advanced_recommendation(age, gender, weight, height, activity_level, goal,
                            medical_history=None, medications=None,
                            fitness_goal=None, integrate_wearables=False,
                            diet_preferences=None, equipment=None):

    bmi = calc_bmi(weight, height)
    category = bmi_category(bmi)

    plan = {
        "bmi": bmi,
        "category": category,
        "exercise": [],
        "diet": [],
        "notes": []
    }

    # -------------------------
    # Equipment-Based Exercises
    # -------------------------
    equipment = (equipment or "").lower()
    exercises = []

    if "dumbbell" in equipment:
        exercises += [
            "Dumbbell Bench Press",
            "Dumbbell Shoulder Press",
            "Dumbbell Bicep Curls",
            "Dumbbell Squats",
            "Dumbbell Deadlifts"
        ]
    if "barbell" in equipment:
        exercises += [
            "Barbell Squat",
            "Barbell Deadlift",
            "Bench Press",
            "Barbell Row"
        ]
    if "resistance" in equipment or "band" in equipment:
        exercises += [
            "Resistance Band Pull Aparts",
            "Band Rows",
            "Band Squats",
            "Band Bicep Curls"
        ]
    if "machine" in equipment:
        exercises += [
            "Leg Press",
            "Cable Rows",
            "Lat Pulldown",
            "Chest Press Machine"
        ]
    if "treadmill" in equipment or "cycle" in equipment or "cardio" in equipment:
        exercises += [
            "Treadmill Running (20-30 mins)",
            "Stationary Bike (20 mins)",
            "Incline Walk"
        ]
    if "bodyweight" in equipment or equipment == "":
        exercises += [
            "Push-Ups",
            "Bodyweight Squats",
            "Planks",
            "Lunges",
            "Mountain Climbers"
        ]

    # Add based on fitness goal
    goal = (goal or "").lower()
    if "lose" in goal or "weight" in goal:
        exercises = [ex for ex in exercises if "Press" not in ex]  # Focus more on cardio/core
        exercises += ["Jump Rope", "HIIT Session (20 mins)", "Brisk Walking"]
    elif "gain" in goal or "muscle" in goal:
        exercises += ["Progressive Overload Lifts", "Compound Movements", "Protein Recovery"]

    plan["exercise"] = list(set(exercises))[:8]  # limit for display

    # -------------------------
    # Diet Recommendation
    # -------------------------
    diet_pref = (diet_preferences or "").lower()
    if "non" in diet_pref or "non-veg" in diet_pref:
        if "gain" in goal:
            meals = [
                "Breakfast: Omelette + Whole wheat bread + Milk",
                "Lunch: Brown rice + Grilled Chicken + Veggies",
                "Snack: Peanut Butter + Banana",
                "Dinner: Chicken curry + Roti + Salad"
            ]
        elif "lose" in goal:
            meals = [
                "Breakfast: Boiled eggs + Oats + Green tea",
                "Lunch: Grilled fish/chicken + Brown rice + Salad",
                "Snack: Roasted chana or nuts",
                "Dinner: Clear soup + Veg sauté + Chicken breast"
            ]
        else:  # Wellness
            meals = [
                "Breakfast: Scrambled eggs + Fruits",
                "Lunch: Mixed dal + Chicken + Veg curry",
                "Dinner: Paneer tikka + Brown rice + Soup"
            ]
    else:  # Vegetarian / Vegan
        if "gain" in goal:
            meals = [
                "Breakfast: Paneer bhurji + Whole wheat bread + Milk",
                "Lunch: Rajma + Brown rice + Ghee",
                "Snack: Dry fruits + Smoothie",
                "Dinner: Paneer tikka + Roti + Salad"
            ]
        elif "lose" in goal:
            meals = [
                "Breakfast: Oats + Banana + Green tea",
                "Lunch: Moong dal + Brown rice + Veggies",
                "Snack: Roasted chana + Buttermilk",
                "Dinner: Soup + Salad + Light dal"
            ]
        else:  # Wellness
            meals = [
                "Breakfast: Upma/Poha + Milk",
                "Lunch: Khichdi + Curd + Salad",
                "Dinner: Roti + Dal + Veg curry"
            ]

    plan["diet"] = meals

    # -------------------------
    # Notes & Tips
    # -------------------------
    plan["notes"].append(f"Your BMI: {bmi} ({category})")
    if "obese" in category.lower() or "overweight" in category.lower():
        plan["notes"].append("Focus on calorie deficit and daily step target (8k–10k).")
    elif "underweight" in category.lower():
        plan["notes"].append("Add 400–500 kcal/day; focus on calorie-dense meals.")
    else:
        plan["notes"].append("Maintain balance with consistent training & nutrition.")

    if integrate_wearables:
        plan["notes"].append("Sync wearables to track HR, calories & sleep for optimization.")

    if medical_history:
        plan["notes"].append(f"⚕️ Be cautious due to: {medical_history}")

    return plan

# -------------------------
# 4. Gradio Interface
# -------------------------
if gr is not None:
    def generate_plan(name, age, gender, height, weight, activity, goal,
                      medical_history, medications, fitness_goal,
                      integrate_wearables, diet_pref, equipment):
        try:
            age, height, weight = int(age), float(height), float(weight)
        except:
            return "❌ Please enter valid numbers for age, height, and weight."

        plan = advanced_recommendation(age, gender, weight, height, activity, goal,
                                       medical_history, medications,
                                       fitness_goal, integrate_wearables,
                                       diet_pref, equipment)

        color = {"Underweight": "🟡", "Healthy": "🟢", "Overweight": "🟠", "Obese": "🔴"}[plan["category"]]

        output = f"""# 🧬 Personalized Fitness & Nutrition Plan for {name}

**BMI:** {plan['bmi']} ({color} {plan['category']})

---

## 🏋️ Exercise Plan
""" + "\n".join([f"- {ex}" for ex in plan["exercise"]]) + """

---

## 🍽️ Diet Plan
""" + "\n".join([f"- {meal}" for meal in plan["diet"]]) + """

---

## 📝 Notes
""" + "\n".join([f"- {note}" for note in plan["notes"]]) + """

---

⚡ *Tip:* Consistency and gradual improvement matter more than perfection.
"""
        return output

    with gr.Blocks(theme="soft", title="AI Fitness Planner Pro") as demo:
        gr.Markdown("# 🧠 AI-Based Personalized Fitness & Lifestyle (Advanced)\nProvide your details for a tailored plan.")

        with gr.Row():
            with gr.Column():
                name = gr.Textbox(label="Name", value="Student")
                age = gr.Number(label="Age", value=25)
                gender = gr.Radio(["Male", "Female"], label="Gender", value="Male")
                height = gr.Number(label="Height (cm)", value=170)
                weight = gr.Number(label="Weight (kg)", value=65)
                activity = gr.Radio(["low","moderate","high"], label="Activity Level", value="moderate")
                goal = gr.Textbox(label="Goal (lose/gain/maintain)", value="lose")
            with gr.Column():
                medical_history = gr.Textbox(label="Medical History")
                medications = gr.Textbox(label="Medications & Allergies")
                fitness_goal = gr.Radio(["Weight Loss", "Muscle Gain", "Endurance", "Flexibility", "Overall Wellness"],
                                        label="Fitness Goal", value="Overall Wellness")
                integrate = gr.Checkbox(label="Integrate with Wearables?")
                diet_pref = gr.Textbox(label="Diet Preference (e.g. veg, non-veg, vegan, low-carb)")
                equipment = gr.Textbox(label="Available Equipment (e.g. dumbbells, treadmill, bands)")

        btn = gr.Button("✨ Generate Personalized Plan")
        output_box = gr.Markdown(label="Personalized Plan")

        btn.click(generate_plan,
                  [name, age, gender, height, weight, activity, goal,
                   medical_history, medications, fitness_goal,
                   integrate, diet_pref, equipment],
                  output_box)

    demo.launch(share=True)
else:
    print("⚠️ Gradio not available. Install it using: pip install gradio")
