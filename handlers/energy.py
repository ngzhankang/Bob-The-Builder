import json
from pathlib import Path
from datetime import datetime

HPB_FOOD_PATH = Path("foodSearch/foodData.json")
HPB_FOODS = json.load(HPB_FOOD_PATH.open())
MEAL_REALISM = {
    "breakfast": [
        "Bread", "Noodles", "Rice Porridge", "Eggs", "Milk", "Yoghurt", 
        "Fruits", "Cereal", "Oats", "Porridge", "Kaya Toast", "Roti"
    ],
    "lunch": [
        "Rice", "Noodles", "Chicken", "Fish", "Pork", "Beef", "Vegetables", 
        "Tofu", "Curry", "Satay", "Laksa"
    ],
    "dinner": [
        "Rice", "Noodles", "Meat", "Fish", "Vegetables", "Soup", "Stew"
    ],
    "snack": [
        "Nuts", "Yoghurt", "Fruits", "Bread", "Milk", "Cheese"
    ]
}


def diagnose_energy(profile):
    slump = profile.get("SLUMP_CHECK", "no")
    morning = profile.get("MORNING_KICK", "ready to go")
    try:
        water = float(profile.get("HYDRATION_CHECK", 2))
    except Exception:
        water = 0

    issues = []
    # chronic dehydration: https://www.healthhub.sg/health-conditions/dehydration-adults
    if water < 2:
        issues.append("chronic_dehydration")
    if slump == "yes":
        issues.append("afternoon_crash")
    if morning == "groggy":
        issues.append("poor_morning_energy")
    if morning == "hungry":
        issues.append("needs_morning_fuel")

    return issues

def get_user_snacks(profile, max_kcal=250, min_protein=8.0, max_sugar=10.0):
    allergies = [a.strip().lower() for a in profile.get("ALLERGIES", "").split(",") if a]
    snack_groups = ["Nuts", "Yoghurt", "Fruits", "Bread", "Milk", "Cheese", "Cereal"]
    candidates = []
    for name, item in HPB_FOODS.items():
        group = item.get("Food Group", "").lower()
        if not any(sg.lower() in group for sg in snack_groups):
            continue
        if any(word in name.lower() for word in ["beef", "cuttlefish", "chicken breast", "topside"]):
            continue
        if any(allergy in name.lower() for allergy in allergies):
            continue
        nutri = item.get("Nutritional Data", {})
        energy = (nutri.get("Energy (kcal)", {}).get("Per Serving (325ml)") or 
                  nutri.get("Energy (kcal)", {}).get("Per Serving") or 
                  nutri.get("Energy (kcal)", {}).get("Per 100g") or 0)
        protein = (nutri.get("Protein (g)", {}).get("Per Serving (325ml)") or 
                   nutri.get("Protein (g)", {}).get("Per Serving") or 
                   nutri.get("Protein (g)", {}).get("Per 100g") or 0)
        sugar = (nutri.get("Sugar (g)", {}).get("Per Serving (325ml)") or 
                 nutri.get("Sugar (g)", {}).get("Per Serving") or 
                 nutri.get("Sugar (g)", {}).get("Per 100g") or 0)
        if max_kcal >= energy >= 100 and protein >= min_protein and sugar <= max_sugar:
            candidates.append({"name": name, "kcal": energy, "protein": protein, "sugar": sugar})
    candidates.sort(key=lambda x: (-x["protein"], x["kcal"]))
    return candidates[:15]

# get timing based on device
def get_meal_timing(hour=None):
    if hour is None:
        hour = datetime.now().hour

    # logic to check what time is it and deduce what meals to offer
    if 6 <= hour < 9:
        return "breakfast", 0.25
    elif 11 <= hour < 14:
        return "lunch", 0.35
    elif 17 <= hour < 20:
        return "dinner", 0.35
    else:
        return "snack", 0.15
    
# define the various food options, giving consideration to allergies etc.
def get_meal_candidates(profile, meal_context, max_kcal):
    # diet_style = profile.get("DIET_STYLE", "").lower()
    allergies = [a.strip().lower() for a in profile.get("ALLERGIES", "").split(",") if a]
    allowed_groups = MEAL_REALISM.get(meal_context["meal_type"], [])
    candidates = []
    for name, item in HPB_FOODS.items():
        group = item.get("Food Group", "").lower()

        # skip unrealistic food for this meal
        if not any(ag.lower() in group for ag in allowed_groups):
            continue

        # skip allergies
        if any(allergy in name.lower() for allergy in allergies):
            continue

        nutri = item.get("Nutritional Data", {})
        keys = ["Per Serving (325ml)", "Per Serving", "Per 100g"]
        energy = float(next((nutri.get("Energy (kcal)", {}).get(k, 0) for k in keys), 0))
        protein = float(next((nutri.get("Protein (g)", {}).get(k, 0) for k in keys), 0))

        if 50 <= energy <= max_kcal and protein >= 3:  # Reasonable meal components
            candidates.append({
                "name": name,
                "kcal": energy,
                "protein": protein,
                "group": item.get("Food Group", "")
            })
    
        candidates.sort(key=lambda x: (-x["protein"], x["kcal"]))
    return candidates[:20]

# calculate the calorie budget for the current meal
def calculate_meal_budget(profile):
    tdee = float(profile.get("TDEE", 2000))
    goal = profile.get("GOAL", "maintenance").lower()

    meal_type, base_pct = get_meal_timing()

    if goal == "fat loss":
        base_pct *= 0.85
    elif goal == "muscle gain":
        base_pct *= 1.15
    
    budget = int(tdee * base_pct)
    return {
        "meal_type": meal_type,
        "budget_kcal": budget,
        "tdee": tdee,
        "goal": profile.get("GOAL"),
        "diet_style": profile.get("DIET_STYLE", "")
    }