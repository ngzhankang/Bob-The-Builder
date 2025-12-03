import json
from pathlib import Path

HPB_FOOD_PATH = Path("foodSearch/foodData.json")
HPB_FOODS = json.load(HPB_FOOD_PATH.open())

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
    candidates = []
    for name, item in HPB_FOODS.items():
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