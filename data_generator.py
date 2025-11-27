"""
GoodFoods Branch Data Generator

Generates 50-100 branch locations for the GoodFoods restaurant chain
across multiple cities in India. Each branch represents a location of
the same brand with consistent cuisine offerings but varying features.
"""

import json
import random
from datetime import datetime, timedelta

# --- GOODFOODS BRAND CONFIGURATION ---

BRAND_NAME = "GoodFoods"
CUISINE_SPECIALTIES = ["Italian", "North Indian", "Continental", "Asian Fusion"]
PRICE_RANGE = "₹₹₹"  # Premium casual dining
BASE_RATING_RANGE = (4.0, 4.8)  # Consistent quality across chain

# --- LOCATION DATA ---

# Metro cities with multiple branches (5-8 branches each)
METRO_LOCATIONS = {
    "Delhi": [
        ("Connaught Place", ["Rooftop Seating", "Live Music", "Full Bar", "Valet Parking"]),
        ("Saket", ["Mall Location", "Family Friendly", "Kids Play Area", "Wifi"]),
        ("Hauz Khas", ["Lake View", "Outdoor Seating", "Romantic Ambiance", "Full Bar"]),
        ("Rohini", ["Ample Parking", "Family Friendly", "Spacious Dining", "AC"]),
        ("Dwarka", ["Near Metro", "Quick Service", "Family Friendly", "Wifi"]),
        ("Nehru Place", ["Corporate Hub", "Business Lunch", "Wifi", "AC"]),
        ("Rajouri Garden", ["Shopping District", "Family Friendly", "Live Music"]),
        ("Vasant Kunj", ["Premium Location", "Valet Parking", "Full Bar", "Romantic"])
    ],
    "Mumbai": [
        ("Bandra", ["Sea View", "Outdoor Seating", "Celebrity Hotspot", "Full Bar"]),
        ("Andheri", ["Near Airport", "Business Travelers", "Quick Service", "Wifi"]),
        ("Colaba", ["Heritage Building", "Tourist Friendly", "Outdoor Seating", "Full Bar"]),
        ("Powai", ["Lake View", "Romantic Ambiance", "Live Music", "Valet Parking"]),
        ("Thane", ["Mall Location", "Family Friendly", "Spacious", "Kids Area"]),
        ("Juhu", ["Beach Proximity", "Outdoor Seating", "Full Bar", "Romantic"]),
        ("Lower Parel", ["Corporate Hub", "Business Lunch", "Rooftop Bar", "Wifi"])
    ],
    "Bangalore": [
        ("Koramangala", ["Pub Street", "Live Music", "Full Bar", "Late Night"]),
        ("Indiranagar", ["Garden Seating", "Outdoor Dining", "Pet Friendly", "Full Bar"]),
        ("Whitefield", ["IT Hub", "Corporate Lunch", "Wifi", "AC"]),
        ("MG Road", ["Central Location", "Metro Access", "Full Bar", "Rooftop"]),
        ("JP Nagar", ["Family Friendly", "Spacious Dining", "Kids Play Area", "Parking"]),
        ("HSR Layout", ["Rooftop Seating", "Outdoor Dining", "Live Music", "Full Bar"])
    ],
    "Chennai": [
        ("T Nagar", ["Shopping Hub", "Family Friendly", "AC", "Wifi"]),
        ("Velachery", ["Residential Area", "Family Dining", "Parking", "Kids Area"]),
        ("OMR", ["IT Corridor", "Business Lunch", "Wifi", "Quick Service"]),
        ("Nungambakkam", ["Premium Location", "Valet Parking", "Full Bar", "Romantic"]),
        ("Adyar", ["Beach Proximity", "Outdoor Seating", "Family Friendly"])
    ],
    "Hyderabad": [
        ("Banjara Hills", ["Premium Location", "Valet Parking", "Full Bar", "Rooftop"]),
        ("Hitech City", ["IT Hub", "Corporate Lunch", "Wifi", "AC"]),
        ("Gachibowli", ["Corporate Zone", "Business Travelers", "Wifi", "Parking"]),
        ("Jubilee Hills", ["Upscale Dining", "Romantic Ambiance", "Full Bar", "Live Music"])
    ]
}

# Tier-2 cities with fewer branches (2-3 branches each)
TIER2_LOCATIONS = {
    "Pune": [
        ("Koregaon Park", ["Premium Location", "Outdoor Seating", "Full Bar"]),
        ("Hinjewadi", ["IT Park", "Corporate Lunch", "Wifi"]),
        ("Viman Nagar", ["Family Friendly", "Parking", "Spacious"])
    ],
    "Jaipur": [
        ("C-Scheme", ["Central Location", "Tourist Friendly", "Full Bar"]),
        ("Malviya Nagar", ["Family Dining", "Parking", "AC"])
    ],
    "Chandigarh": [
        ("Sector 17", ["Shopping Hub", "Family Friendly", "AC"]),
        ("Elante Mall", ["Mall Location", "Kids Area", "Wifi"])
    ],
    "Lucknow": [
        ("Hazratganj", ["Heritage Area", "Tourist Friendly", "AC"]),
        ("Gomti Nagar", ["Upscale Dining", "Valet Parking", "Full Bar"])
    ],
    "Ahmedabad": [
        ("SG Highway", ["Corporate Zone", "Business Lunch", "Wifi"]),
        ("CG Road", ["Shopping District", "Family Friendly", "AC"])
    ]
}

# Tier-3 cities with single branches
TIER3_LOCATIONS = {
    "Indore": [("Vijay Nagar", ["Family Friendly", "AC", "Parking"])],
    "Mysore": [("Saraswati Puram", ["Tourist Friendly", "Heritage View", "AC"])],
    "Coimbatore": [("RS Puram", ["Family Dining", "Parking", "Wifi"])],
    "Nashik": [("College Road", ["Family Friendly", "AC", "Spacious"])],
    "Surat": [("Athwa", ["Family Dining", "AC", "Parking"])],
    "Vadodara": [("Alkapuri", ["Central Location", "Family Friendly", "AC"])],
    "Kochi": [("MG Road", ["Waterfront View", "Outdoor Seating", "Full Bar"])],
    "Visakhapatnam": [("Beach Road", ["Sea View", "Outdoor Seating", "Romantic"])],
    "Bhubaneswar": [("Sahid Nagar", ["Family Friendly", "AC", "Parking"])],
    "Guwahati": [("GS Road", ["Central Location", "Family Dining", "AC"])]
}

# --- HELPER FUNCTIONS ---

def get_standard_schedule():
    """Generate standard operating hours (10:00 AM - 11:00 PM) with 30-minute slots"""
    slots = []
    start_hour = 10
    end_hour = 23
    
    current = datetime(2000, 1, 1, start_hour, 0)
    end = datetime(2000, 1, 1, end_hour, 0)
    
    while current <= end:
        slots.append(current.strftime("%H:%M"))
        current += timedelta(minutes=30)
    
    week_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return {day: slots for day in week_days}

def generate_capacity(location_type):
    """Generate seating capacity based on location type"""
    if location_type == "metro":
        return random.randint(80, 200)  # Larger metro branches
    elif location_type == "tier2":
        return random.randint(50, 120)  # Medium tier-2 branches
    else:  # tier3
        return random.randint(30, 80)   # Smaller tier-3 branches

def add_common_features(specific_features):
    """Add common features that all GoodFoods branches have"""
    common = ["Professional Staff", "Clean & Hygienic", "Card Payment"]
    return list(set(specific_features + common))

# --- MAIN GENERATION FUNCTION ---

def generate_goodfoods_branches():
    """Generate all GoodFoods branch locations"""
    branches = []
    branch_id = 1
    
    standard_schedule = get_standard_schedule()
    
    # Generate Metro city branches
    for city, locations in METRO_LOCATIONS.items():
        for locality, features in locations:
            branches.append({
                "id": branch_id,
                "branch_name": f"{BRAND_NAME} - {locality}",
                "city": city,
                "locality": locality,
                "full_address": f"{locality}, {city}",
                "cuisine_specialties": CUISINE_SPECIALTIES,
                "price_range": PRICE_RANGE,
                "rating": round(random.uniform(*BASE_RATING_RANGE), 1),
                "capacity": generate_capacity("metro"),
                "features": add_common_features(features),
                "weekly_schedule": standard_schedule,
                "branch_type": "Metro"
            })
            branch_id += 1
    
    # Generate Tier-2 city branches
    for city, locations in TIER2_LOCATIONS.items():
        for locality, features in locations:
            branches.append({
                "id": branch_id,
                "branch_name": f"{BRAND_NAME} - {locality}",
                "city": city,
                "locality": locality,
                "full_address": f"{locality}, {city}",
                "cuisine_specialties": CUISINE_SPECIALTIES,
                "price_range": PRICE_RANGE,
                "rating": round(random.uniform(*BASE_RATING_RANGE), 1),
                "capacity": generate_capacity("tier2"),
                "features": add_common_features(features),
                "weekly_schedule": standard_schedule,
                "branch_type": "Tier-2"
            })
            branch_id += 1
    
    # Generate Tier-3 city branches
    for city, locations in TIER3_LOCATIONS.items():
        for locality, features in locations:
            branches.append({
                "id": branch_id,
                "branch_name": f"{BRAND_NAME} - {locality}",
                "city": city,
                "locality": locality,
                "full_address": f"{locality}, {city}",
                "cuisine_specialties": CUISINE_SPECIALTIES,
                "price_range": PRICE_RANGE,
                "rating": round(random.uniform(*BASE_RATING_RANGE), 1),
                "capacity": generate_capacity("tier3"),
                "features": add_common_features(features),
                "weekly_schedule": standard_schedule,
                "branch_type": "Tier-3"
            })
            branch_id += 1
    
    return branches

# --- MAIN EXECUTION ---

if __name__ == "__main__":
    branches = generate_goodfoods_branches()
    
    # Save to JSON
    with open('d:/assign/goodfoods_branches.json', 'w', encoding='utf-8') as f:
        json.dump(branches, f, indent=2, ensure_ascii=False)
    
    # Print summary statistics
    print(f"✅ Generated {len(branches)} GoodFoods branch locations")
    print(f"\n📊 Distribution:")
    print(f"   Metro cities: {sum(1 for b in branches if b['branch_type'] == 'Metro')} branches")
    print(f"   Tier-2 cities: {sum(1 for b in branches if b['branch_type'] == 'Tier-2')} branches")
    print(f"   Tier-3 cities: {sum(1 for b in branches if b['branch_type'] == 'Tier-3')} branches")
    print(f"\n🌍 Geographic Coverage:")
    cities = set(b['city'] for b in branches)
    print(f"   Total cities: {len(cities)}")
    print(f"   Cities: {', '.join(sorted(cities))}")
    print(f"\n💺 Capacity Range: {min(b['capacity'] for b in branches)} - {max(b['capacity'] for b in branches)} seats")
    print(f"   Average capacity: {sum(b['capacity'] for b in branches) // len(branches)} seats")
    print(f"\n⭐ Rating Range: {min(b['rating'] for b in branches)} - {max(b['rating'] for b in branches)}")
    print(f"\n📁 Saved to: d:/assign/goodfoods_branches.json")
