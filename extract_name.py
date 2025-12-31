import json
import os

def extract_sorted_meals(root_folder, output_filename):
    unique_meals_dict = {}
    files_processed = 0
    
    print(f"\n--- Scanning folders in: {root_folder} ---")

    for dirpath, _, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.lower().endswith('.json'):
                file_path = os.path.join(dirpath, filename)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    if isinstance(data, dict) and "meals" in data and isinstance(data["meals"], list):
                        
                        for meal in data["meals"]:
                            if isinstance(meal, dict) and "name" in meal:
                                name = meal["name"]
                                
                                if not name:
                                    continue

                                clean_key = name.strip().lower()
                                
                                # Duplicate Check
                                if clean_key not in unique_meals_dict:
                                    
                                    nutrition = meal.get("nutrition")
                                    ingredients = meal.get("ingredients")
                                    
                                    meal_entry = {
                                        "name": name.strip()
                                    }

                                    # Logic: Nutrition hai toh wo daalo, warna ingredients
                                    if nutrition and str(nutrition).strip() != "":
                                        meal_entry["nutrition"] = nutrition
                                        # Sorting ke liye ek hidden tag lagaya hai 'type': 1
                                        meal_entry["_sort_order"] = 1 
                                    else:
                                        meal_entry["ingredients"] = ingredients
                                        # Ingredients walon ka tag 'type': 2 (taake wo baad mein aayen)
                                        meal_entry["_sort_order"] = 2
                                    
                                    unique_meals_dict[clean_key] = meal_entry

                    files_processed += 1
                    print(f"Processed: {filename}...", end='\r')

                except Exception as e:
                    print(f"\nError in {filename}: {e}")

    # Convert dict to list
    final_list = list(unique_meals_dict.values())

    # --- SORTING MAGIC ---
    # Python ko bata rahe hain ke '_sort_order' key ke hisaab se line up karo.
    # 1 wala pehle aayega (Nutrition), 2 wala baad mein (Ingredients).
    final_list.sort(key=lambda x: x["_sort_order"])

    # Clean up: Save karne se pehle wo '_sort_order' wala tag hata dete hain, user ko uski zaroorat nahi.
    for item in final_list:
        del item["_sort_order"]

    # Save File
    if final_list:
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(final_list, f, indent=4)
        
        print(f"\n\n--- Done! ---")
        print(f"Total Unique Meals: {len(final_list)}")
        print(f"Sorted & Saved to: {output_filename}")
    else:
        print("\nNo meals found.")

# --- Run ---
if __name__ == "__main__":
    target_directory = input("Enter path to parent folder: ").strip()
    
    if target_directory.startswith('"') and target_directory.endswith('"'):
        target_directory = target_directory[1:-1]

    if os.path.exists(target_directory):
        extract_sorted_meals(target_directory, "sorted_meals_data.json")
    else:
        print("Error: Directory not found.")