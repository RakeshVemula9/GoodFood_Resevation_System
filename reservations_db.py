"""
Reservations Database Manager

Handles storing and retrieving reservation data for GoodFoods.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional

RESERVATIONS_FILE = "d:/assign/reservations.json"

def load_reservations() -> List[Dict]:
    """Load all reservations from the database file."""
    if not os.path.exists(RESERVATIONS_FILE):
        return []
    
    try:
        with open(RESERVATIONS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_reservation(reservation: Dict) -> bool:
    """Save a new reservation to the database."""
    try:
        reservations = load_reservations()
        reservations.append(reservation)
        
        with open(RESERVATIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(reservations, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        print(f"Error saving reservation: {e}")
        return False

def get_reservation(reservation_id: str) -> Optional[Dict]:
    """Retrieve a specific reservation by ID."""
    reservations = load_reservations()
    return next((r for r in reservations if r['reservation_id'] == reservation_id), None)

def get_all_reservations() -> List[Dict]:
    """Get all reservations."""
    return load_reservations()
