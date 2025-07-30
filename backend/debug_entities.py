#!/usr/bin/env python3
"""Debug entity extraction"""

import re

message = "What's the current inventory status in the Maternity Ward?"
message_lower = message.lower()

print(f"Original message: {message}")
print(f"Lowercase message: {message_lower}")

# Test the patterns
location_patterns = [
    r'\b(?:in|from|at)\s+([A-Z]{2,}-?\d*)\b',
    r'\b(ICU|Surgery|Pharmacy|Lab|Warehouse)(?:-\d+)?\b',
    r'\b(ER)(?![a-z])(?:-\d+)?\b'  # More specific ER pattern to avoid matching inside words
]

print("\nTesting patterns:")
for i, pattern in enumerate(location_patterns):
    print(f"\nPattern {i+1}: {pattern}")
    matches = re.findall(pattern, message, re.IGNORECASE)
    print(f"Matches: {matches}")

# Test a word boundary check
entities = []
common_entities = ["ICU", "ER", "Surgery", "Pharmacy", "Laboratory", "Warehouse", "Maternity", "Ward"]
for entity in common_entities:
    # Use word boundaries to avoid matching partial words
    pattern = r'\b' + re.escape(entity.lower()) + r'\b'
    if re.search(pattern, message_lower):
        entities.append(entity)
        print(f"Found entity '{entity}' in message")

print(f"\nFinal entities: {entities}")
