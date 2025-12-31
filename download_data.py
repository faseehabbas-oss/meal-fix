import firebase_admin
from firebase_admin import credentials, firestore
import json
import os
import re  # Added for cleaning filenames

# --- 1. SETUP ---
if not firebase_admin._apps:
    # Make sure this path matches your file exactly
    cred = credentials.Certificate("./redge-fit-firebase-adminsdk-jbdq0-e031bd64c8.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# --- CONFIGURATION ---
ROOT_COLLECTION_NAME = 'vegeterianPlan'
SUB_COLLECTION_NAME = 'mealPlans'
EXPORT_FOLDER_NAME = 'vegeterian_plans'

base_output_folder = "exported_meal_plans"
target_dir = os.path.join(base_output_folder, EXPORT_FOLDER_NAME)
os.makedirs(target_dir, exist_ok=True)

print(f"🚀 Starting export for '{ROOT_COLLECTION_NAME}'...")

# --- HELPER FUNCTION: CLEAN FILENAME ---
def sanitize_filename(name):
    """
    Removes characters that are not allowed in filenames (like /, ?, <, >, :, etc.)
    Replaces spaces with underscores.
    """
    # Remove anything that isn't a letter, number, space, dash, or underscore
    s = re.sub(r'[^a-zA-Z0-9 \-_]', '', str(name))
    # Replace spaces with underscores
    return s.replace(' ', '_')

# --- 2. MAIN LOGIC ---
root_collection = db.collection(ROOT_COLLECTION_NAME)
root_docs = root_collection.stream()

processed_count = 0

for plan_doc in root_docs:
    plan_id = plan_doc.id
    plan_data = plan_doc.to_dict()
    
    # --- GET HUMAN READABLE NAME ---
    # Try to find a 'name' or 'title' field. If not found, fall back to the ID.
    raw_name = plan_data.get('name', plan_data.get('title', plan_id))
    safe_name = sanitize_filename(raw_name)
    
    # Prepare list for meals
    meals_data = []
    
    print(f"--> Processing: {safe_name} (ID: {plan_id})")

    meals_ref = plan_doc.reference.collection(SUB_COLLECTION_NAME)
    meal_docs = meals_ref.stream()

    for meal in meal_docs:
        m_data = meal.to_dict()
        # m_data['__doc_id'] = meal.id # Uncomment if needed
        meals_data.append(m_data)

    full_plan_export = {
        "plan_id": plan_id,
        "type": ROOT_COLLECTION_NAME,
        "plan_details": plan_data,
        "meals": meals_data,
    }

    # --- 4. SAVE WITH READABLE NAME ---
    # Result example: exported_meal_plans/standard_plans/Keto_Day_1.json
    filename = os.path.join(target_dir, f"{safe_name}.json")
    
    # Handle duplicate names (e.g. if you have two plans named "Keto Day 1")
    if os.path.exists(filename):
        filename = os.path.join(target_dir, f"{safe_name}_{plan_data.mealPlan}.json")
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(full_plan_export, f, ensure_ascii=False, indent=4)
    
    processed_count += 1

print("------------------------------------------------")
print(f"✅ DONE! Exported {processed_count} plans.")
print(f"📁 Files saved in: {target_dir}")