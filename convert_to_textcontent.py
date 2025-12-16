#!/usr/bin/env python3
"""Convert JSON files from shorthand to proper modala format with textcontent."""

import json
import re
import sys
from pathlib import Path


def convert_element(obj):
    """Recursively convert shorthand elements to textcontent format."""
    if not isinstance(obj, dict):
        return obj
    
    # List of HTML elements that should use textcontent
    text_elements = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li', 'td', 'th', 
                     'span', 'strong', 'em', 'label', 'option', 'button']
    
    result = {}
    for key, value in obj.items():
        # Check if this is a shorthand text element
        if key in text_elements and isinstance(value, str):
            # Convert to proper format: "h2": "text" -> "h2": {"textcontent": "text"}
            result[key] = {"textcontent": value}
        
        # Check for elements with "text" property that should be "textcontent"
        elif isinstance(value, dict):
            new_value = {}
            for inner_key, inner_value in value.items():
                if inner_key == "text" and not (key in ['textarea', 'input', 'select']):
                    # Change "text" to "textcontent" (except for form elements)
                    new_value["textcontent"] = inner_value
                elif inner_key == "children" and isinstance(inner_value, list):
                    # Recursively process children
                    new_value[inner_key] = [convert_element(child) for child in inner_value]
                elif isinstance(inner_value, dict):
                    new_value[inner_key] = convert_element(inner_value)
                elif isinstance(inner_value, list):
                    new_value[inner_key] = [convert_element(item) if isinstance(item, dict) else item for item in inner_value]
                else:
                    new_value[inner_key] = inner_value
            result[key] = new_value
        
        elif isinstance(value, list):
            # Recursively process lists
            result[key] = [convert_element(item) if isinstance(item, dict) else item for item in value]
        else:
            result[key] = value
    
    return result


def convert_file(filepath):
    """Convert a JSON file to use proper textcontent format."""
    print(f"Converting {filepath}...")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        converted = convert_element(data)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(converted, f, indent=4, ensure_ascii=False)
        
        print(f"✅ Successfully converted {filepath}")
        return True
    except Exception as e:
        print(f"❌ Error converting {filepath}: {e}")
        return False


def main():
    """Main entry point."""
    base_path = Path(r"c:\Users\g0d77\New folder\dotFly\demo_app\pages\tutorial")
    
    files = [
        base_path / "csv_demo.json",
        base_path / "carousel_demo.json",
        base_path / "modala_demo.json",
        base_path / "advanced.json"
    ]
    
    success_count = 0
    for filepath in files:
        if filepath.exists():
            if convert_file(filepath):
                success_count += 1
        else:
            print(f"⚠️ File not found: {filepath}")
    
    print(f"\n{'='*50}")
    print(f"Converted {success_count}/{len(files)} files successfully")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
