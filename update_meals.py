import json
import os

CONFIG_FILE = "path_config.json"

def save_path_config(path):
    """Path ko file mein save karta hai taake agli baar yaad rahe"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump({"last_path": path}, f)
    except Exception as e:
        print(f"Warning: Could not save path config. {e}")

def load_path_config():
    """Saved path ko load karta hai"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("last_path", "")
        except:
            return ""
    return ""

def update_meal_records(root_folder, meal_name, new_calories, new_protein):
    files_modified = 0
    records_updated = 0
    records_skipped = 0
    
    target_name_lower = meal_name.strip().lower()

    print(f"\n--- Searching for meal: '{meal_name}' ---")
    
    # Scanning logic
    for dirpath, _, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.lower().endswith('.json') and filename != CONFIG_FILE:
                file_path = os.path.join(dirpath, filename)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    file_changed = False
                    
                    if isinstance(data, dict) and "meals" in data and isinstance(data["meals"], list):
                        
                        for meal in data["meals"]:
                            if isinstance(meal, dict) and "name" in meal and meal["name"]:
                                
                                if meal["name"].strip().lower() == target_name_lower:
                                    
                                    current_cal = meal.get("calories")
                                    current_prot = meal.get("protein")
                                    folder_name = os.path.basename(dirpath)

                                    if current_cal == new_calories and current_prot == new_protein:
                                        print(f"[SKIP] {filename} (Already Updated)")
                                        records_skipped += 1
                                    else:
                                        print(f"[UPDATE] {filename} in [{folder_name}]")
                                        print(f"       Old: {current_cal} Cal | {current_prot} Prot")
                                        
                                        meal["calories"] = new_calories
                                        meal["protein"] = new_protein
                                        
                                        print(f"       New: {new_calories} Cal | {new_protein} Prot")
                                        file_changed = True
                                        records_updated += 1

                    if file_changed:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            json.dump(data, f, indent=4)
                        files_modified += 1

                except Exception as e:
                    pass 

    print("-" * 30)
    print(f"Done: {records_updated} Updated | {records_skipped} Skipped")

# --- SMART USER INPUT SECTION ---
if __name__ == "__main__":
    
    # 1. Path Setup (Sirf ek dafa chalega)
    saved_path = load_path_config()
    final_path = ""

    if saved_path and os.path.exists(saved_path):
        print(f"\nSaved Path found: {saved_path}")
        use_saved = input("Press ENTER to use this path (or type a new one): ").strip()
        
        if use_saved == "":
            final_path = saved_path
        else:
            final_path = use_saved
    else:
        final_path = input("Enter path to parent folder: ").strip()

    if final_path.startswith('"') and final_path.endswith('"'):
        final_path = final_path[1:-1]

    if os.path.exists(final_path):
        if final_path != saved_path:
            save_path_config(final_path)

        print("\n" + "="*40)
        print("STARTING CONTINUOUS MODE")
        print("To STOP: Type 'exit' or press Enter on Meal Name.")
        print("="*40)

        # 2. CONTINUOUS LOOP (Ye baar baar chalega)
        while True:
            print("\n" + "..."*10)
            target_meal = input("Enter Meal Name to find: ").strip()
            
            # --- EXIT CONDITION ---
            if target_meal.lower() in ["exit", "quit", ""]:
                print("Exiting script. Goodbye!")
                break
            
            while True:
                try:
                    target_cal = int(input(f"Enter new Calories for '{target_meal}': "))
                    target_prot = float(input(f"Enter new Protein for '{target_meal}': "))
                    break
                except ValueError:
                    print("Invalid number. Please enter digits only.")

            # Update run karein
            update_meal_records(final_path, target_meal, target_cal, target_prot)
            
            # Yahan loop wapis upar jayega aur naya naam maangega
            
    else:
        print(f"Error: Path '{final_path}' does not exist.")