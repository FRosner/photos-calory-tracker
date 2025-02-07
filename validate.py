import json
import os
from pathlib import Path
from typing import Dict, Any

from main import analyze_images, FoodAnalysisResponse


def load_test_case(image_path: Path) -> tuple[bytes, Dict[str, Any]]:
    print(f"Loading {image_path.name}")
    with open(image_path, 'rb') as f:
        image_data = f.read()
    
    json_path = image_path.with_suffix('.json')
    print(f"Loading {json_path.name}")
    with open(json_path, 'r') as f:
        expected = json.load(f)
    
    return image_data, expected


def compare_analysis(actual: FoodAnalysisResponse, expected: Dict[str, Any]) -> Dict[str, Any]:
    if not actual or not actual.foods:
        return {"error": "No analysis produced"}
    
    differences = {}
    actual_food = actual.foods[0]  # Assuming single food item per image for simplicity
    expected_food = expected["foods"][0]
    
    fields_to_compare = [
        "protein_g", "fat_g", "carbohydrate_g", "total_mass_g", 
        "total_kcal", "total_health_score"
    ]
    
    for field in fields_to_compare:
        actual_value = getattr(actual_food, field)
        expected_value = expected_food[field]
        if actual_value != expected_value:
            differences[field] = {
                "actual": actual_value,
                "expected": expected_value,
                "difference": actual_value - expected_value
            }
    
    # Compare string fields
    for field in ["readable_name", "processing_degree"]:
        actual_value = getattr(actual_food, field)
        expected_value = expected_food[field]
        if actual_value != expected_value:
            differences[field] = {
                "actual": actual_value,
                "expected": expected_value
            }
    
    # Compare components list
    actual_components = set(actual_food.components)
    expected_components = set(expected_food["components"])
    if actual_components != expected_components:
        differences["components"] = {
            "actual": list(actual_components),
            "expected": list(expected_components),
            "missing": list(expected_components - actual_components),
            "unexpected": list(actual_components - expected_components)
        }
    
    return differences


def main():
    validation_dir = Path("validation")
    if not validation_dir.exists():
        print(f"Validation directory {validation_dir} does not exist")
        return

    for image_path in validation_dir.glob("*.jpg"):
        print(f"\nValidating {image_path.name}")
        try:
            image_data, expected = load_test_case(image_path)
            actual = analyze_images([image_data])
            
            differences = compare_analysis(actual, expected)
            if differences:
                print("Differences found:")
                print(json.dumps(differences, indent=2))
            else:
                print("No differences found - test passed!")
                
        except Exception as e:
            print(f"Error processing {image_path.name}: {e}")


if __name__ == "__main__":
    main()