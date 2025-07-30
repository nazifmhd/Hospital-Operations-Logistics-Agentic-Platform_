#!/usr/bin/env python3
"""Debug location mapping"""

def test_location_mapping():
    location_name = "maternity ward"
    location_search = location_name.lower().strip()
    print(f"Original location_name: {location_name}")
    print(f"Location search: {location_search}")
    
    # Common location name mappings
    location_mappings = {
        "clinical laboratory": ["clinical laboratory", "lab", "laboratory", "clinical lab"],
        "icu": ["icu", "intensive care", "intensive care unit", "icu-01"],
        "er": ["er", "emergency", "emergency room", "er-01"],
        "surgery": ["surgery", "surgical", "operating room", "or", "surgery-01"],
        "pharmacy": ["pharmacy", "pharmaceutical", "pharmacy-01"],
        "warehouse": ["warehouse", "storage", "main storage"],
        "maternity ward": ["maternity ward", "maternity", "maternity-01", "birthing", "obstetrics"]
    }
    
    original_location_name = location_name
    # Try to find the best matching location
    import re
    for standard_location, variants in location_mappings.items():
        print(f"\nChecking standard_location: {standard_location}")
        print(f"Variants: {variants}")
        for variant in variants:
            # Use word boundaries to avoid partial matches like "er" in "maternity"
            pattern = r'\b' + re.escape(variant) + r'\b'
            match_result = re.search(pattern, location_search)
            print(f"  Testing pattern '{pattern}' against '{location_search}': {bool(match_result)}")
            if match_result:
                print(f"MATCH FOUND: {standard_location}")
                location_name = standard_location
                break
        if location_name == standard_location:  # Found a match, break outer loop
            break
    
    print(f"\nFinal location_name: {location_name}")
    print(f"Changed from original: {original_location_name != location_name}")

if __name__ == "__main__":
    test_location_mapping()
