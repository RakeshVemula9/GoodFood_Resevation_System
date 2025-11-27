"""
GoodFoods Reservation Agent Core

Implements the AI agent for GoodFoods restaurant chain reservations.
Uses Model Context Protocol (MCP) for tool calling and llama-3.3-8b via Groq API.
"""

import os
import json
import requests
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Import MCP server
from mcp_server import create_mcp_server

# --- GOODFOODS BRANCH DATA LOADER ---

def load_branches() -> List[Dict[str, Any]]:
    """
    Load GoodFoods branch data from JSON file
    
    Returns:
        List of branch dictionaries with all location data
    """
    try:
        with open('d:/assign/goodfoods_branches.json', 'r', encoding='utf-8') as f:
            branches = json.load(f)
        print(f"✅ Loaded {len(branches)} GoodFoods branches")
        return branches
    except FileNotFoundError:
        print("❌ Error: goodfoods_branches.json not found. Run data_generator.py first.")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON: {e}")
        return []

# Global branches data
BRANCHES = load_branches()

# --- RESERVATION TOOLS ---

def search_branches(
    city: Optional[str] = None,
    locality: Optional[str] = None,
    features: Optional[List[str]] = None,
    min_rating: Optional[float] = None,
    min_capacity: Optional[int] = None
) -> str:
    """
    Search for GoodFoods branches based on criteria
    
    Args:
        city: City name filter
        locality: Locality/neighborhood filter
        features: Required features (e.g., ['Rooftop Seating', 'Live Music'])
        min_rating: Minimum rating filter
        min_capacity: Minimum seating capacity filter
        
    Returns:
        Formatted string with matching branches
    """
    results = []
    
    for branch in BRANCHES:
        match = True
        
        # City filter
        if city and city.lower() not in branch['city'].lower():
            match = False
        
        # Locality filter
        if locality and locality.lower() not in branch['locality'].lower():
            match = False
        
        # Features filter (all requested features must be present)
        if features:
            branch_features_lower = [f.lower() for f in branch['features']]
            for required_feature in features:
                if required_feature.lower() not in branch_features_lower:
                    match = False
                    break
        
        # Rating filter
        if min_rating and branch['rating'] < min_rating:
            match = False
        
        # Capacity filter
        if min_capacity and branch['capacity'] < min_capacity:
            match = False
        
        if match:
            results.append(branch)
    
    # Return results
    if not results:
        return "No GoodFoods branches found matching your criteria. Try broadening your search."
    
    # Limit to top 5 results
    results = results[:5]
    
    output = f"Found {len(results)} GoodFoods branch(es):\n\n"
    for branch in results:
        output += f"📍 **{branch['branch_name']}** (ID: {branch['id']})\n"
        output += f"   Location: {branch['full_address']}\n"
        output += f"   Rating: {branch['rating']}⭐ | Capacity: {branch['capacity']} seats\n"
        output += f"   Features: {', '.join(branch['features'][:5])}\n"
        output += f"   Cuisines: {', '.join(branch['cuisine_specialties'])}\n\n"
    
    return output


def get_recommendations(preferences: str) -> str:
    """
    Get intelligent branch recommendations based on user preferences
    
    Args:
        preferences: Natural language description of preferences
        
    Returns:
        Formatted string with top 3 recommendations
    """
    # Tokenize preferences
    keywords = preferences.lower().split()
    
    scored_branches = []
    
    for branch in BRANCHES:
        score = 0
        
        # Create searchable text from branch data
        searchable_text = (
            f"{branch['branch_name']} {branch['city']} {branch['locality']} "
            f"{' '.join(branch['features'])} {' '.join(branch['cuisine_specialties'])}"
        ).lower()
        
        # Keyword matching
        for keyword in keywords:
            if keyword in searchable_text:
                score += 1
        
        # Bonus for high ratings
        score += branch['rating'] / 5.0  # Add 0.0-1.0 based on rating
        
        # Bonus for features match
        branch_features_lower = [f.lower() for f in branch['features']]
        for pref_word in keywords:
            if any(pref_word in feature for feature in branch_features_lower):
                score += 0.5
        
        if score > 0:
            scored_branches.append((score, branch))
    
    # Sort by score
    scored_branches.sort(key=lambda x: x[0], reverse=True)
    
    if not scored_branches:
        return "I couldn't find specific recommendations based on those preferences. Try searching for branches in your preferred city instead!"
    
    # Top 3 recommendations
    top_branches = scored_branches[:3]
    
    output = "Based on your preferences, I recommend these GoodFoods branches:\n\n"
    for rank, (score, branch) in enumerate(top_branches, 1):
        output += f"{rank}. **{branch['branch_name']}**\n"
        output += f"   📍 {branch['full_address']}\n"
        output += f"   ⭐ {branch['rating']} rating | 💺 {branch['capacity']} seats\n"
        output += f"   ✨ Highlights: {', '.join(branch['features'][:3])}\n\n"
    
    return output


def make_reservation(
    date: str,
    time: str,
    party_size: int,
    branch_id: Optional[int] = None,
    branch_name: Optional[str] = None,
    city: Optional[str] = None,
    customer_name: Optional[str] = None,
    customer_phone: Optional[str] = None,
    occasion: Optional[str] = None
) -> str:
    """
    Make a reservation at a GoodFoods branch
    
    Args:
        date: Reservation date (YYYY-MM-DD)
        time: Reservation time (HH:MM)
        party_size: Number of people
        branch_id: Branch ID (optional if branch_name provided)
        branch_name: Branch name (optional if branch_id provided)
        city: City name (helps disambiguate branch_name)
        customer_name: Customer's full name
        customer_phone: Customer's phone number
        occasion: Occasion for booking (birthday, anniversary, etc.)
        
    Returns:
        Confirmation message or error message
    """
    branch = None
    
    # Convert empty string or 0 to None for branch_id
    if branch_id == "" or branch_id == 0:
        branch_id = None
    
    # Find branch by ID
    if branch_id:
        branch = next((b for b in BRANCHES if b['id'] == int(branch_id)), None)
    
    # Find branch by name
    if not branch and branch_name:
        matches = []
        for b in BRANCHES:
            name_match = branch_name.lower() in b['branch_name'].lower()
            locality_match = branch_name.lower() in b['locality'].lower()
            
            if name_match or locality_match:
                # If city specified, must match
                if city and city.lower() in b['city'].lower():
                    matches.append(b)
                elif not city:
                    matches.append(b)
        
        if len(matches) == 1:
            branch = matches[0]
        elif len(matches) > 1:
            branch_list = '\n'.join([f"  - {m['branch_name']} (ID: {m['id']})" for m in matches[:5]])
            return f"Multiple branches found matching '{branch_name}':\n{branch_list}\n\nPlease specify the exact branch or use the ID."
    
    if not branch:
        return f"❌ Branch not found. Please provide a valid branch ID or exact branch name. Use search_branches to find available locations."
    
    # Validate date format
    try:
        reservation_date = datetime.strptime(date, "%Y-%m-%d")
        day_name = reservation_date.strftime("%A")
    except ValueError:
        return f"❌ Invalid date format. Please use YYYY-MM-DD (e.g., 2025-12-25)"
    
    # Check if date is in the past
    today = datetime.now().date()
    if reservation_date.date() < today:
        return f"❌ Cannot make reservations for past dates. Please choose a future date."
    
    # Check availability (using weekly schedule)
    schedule = branch.get('weekly_schedule', {})
    available_slots = schedule.get(day_name, [])
    
    if not available_slots:
        return f"❌ {branch['branch_name']} is closed on {day_name}s."
    
    if time not in available_slots:
        sample_slots = ', '.join(available_slots[::4][:5])  # Show every 4th slot (2-hour intervals)
        return f"❌ {branch['branch_name']} is not available at {time} on {day_name}s.\n   Available times: {sample_slots} (and more)"
    
    # Check capacity
    if party_size > branch['capacity']:
        return f"❌ Party size ({party_size}) exceeds branch capacity ({branch['capacity']} seats). Please contact us directly for large party arrangements."
    
    if party_size < 1:
        return f"❌ Invalid party size. Must be at least 1 person."
    
    # Request customer details if not provided
    if not customer_name or not customer_phone:
        return f"📝 To complete your reservation, please provide:\n  1. Your full name\n  2. Contact phone number\n  3. Occasion (optional: birthday, anniversary, date night, etc.)\n\nExample: 'John Doe, 9876543210, birthday celebration'"
    
    # Generate reservation ID and table number
    reservation_id = f"GF-{random.randint(10000, 99999)}"
    table_number = random.randint(1, min(20, branch['capacity'] // 4))
    
    # Create reservation record
    reservation_data = {
        "reservation_id": reservation_id,
        "customer_name": customer_name,
        "customer_phone": customer_phone,
        "occasion": occasion or "Not specified",
        "branch_id": branch['id'],
        "branch_name": branch['branch_name'],
        "branch_location": branch['full_address'],
        "date": date,
        "day_of_week": day_name,
        "time": time,
        "party_size": party_size,
        "table_number": table_number,
        "created_at": datetime.now().isoformat(),
        "status": "confirmed"
    }
    
    # Save to database
    try:
        from reservations_db import save_reservation
        save_reservation(reservation_data)
    except Exception as e:
        print(f"Warning: Could not save to database: {e}")
    
    # Generate confirmation message
    confirmation = f"✅ **RESERVATION SUCCESSFULLY CONFIRMED!**\n\n"
    confirmation += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    confirmation += f"🎫 **Reservation ID:** {reservation_id}\n\n"
    confirmation += f"👤 **Guest Name:** {customer_name}\n"
    confirmation += f"📞 **Contact:** {customer_phone}\n"
    if occasion and occasion != "Not specified":
        confirmation += f"🎉 **Occasion:** {occasion}\n"
    confirmation += f"\n🍽️ **Restaurant:** {branch['branch_name']}\n"
    confirmation += f"📍 **Address:** {branch['full_address']}\n\n"
    confirmation += f"📅 **Date:** {reservation_date.strftime('%A, %B %d, %Y')}\n"
    confirmation += f"🕐 **Time:** {time}\n"
    confirmation += f"👥 **Party Size:** {party_size} people\n"
    confirmation += f"🪑 **Table Number:** {table_number}\n\n"
    confirmation += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    confirmation += f"💡 **Please Note:**\n"
    confirmation += f"  • Arrive 10-15 minutes early\n"
    confirmation += f"  • Quote reservation ID: {reservation_id}\n"
    confirmation += f"  • Call us for modifications or cancellations\n\n"
    confirmation += f"Looking forward to serving you at GoodFoods! 🌟"
    
    return confirmation


# --- AI AGENT ---

class Agent:
    """
    GoodFoods AI Reservation Agent
    
    Uses llama-3.3-8b via Groq API with MCP protocol for tool calling
    """
    
    def __init__(
        self,
        api_key: str,
        model: str = "llama-3.1-8b-instant",
        base_url: str = "https://api.groq.com/openai/v1"
    ):
        """
        Initialize the agent
        
        Args:
            api_key: Groq API key
            model: Model name (default: llama-3.3-8b-instant)
            base_url: API base URL
        """
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        
        # Initialize MCP server
        import sys
        self.mcp_server = create_mcp_server(sys.modules[__name__])
        
        # Get tools in OpenAI format (Groq uses OpenAI-compatible API)
        self.tools = self.mcp_server.to_openai_format()
        
        # Initialize conversation history
        self.history = [
            {"role": "system", "content": f"""You are an AI assistant for GoodFoods, a premium casual dining restaurant chain with 50+ branches across India.

**Your Role:**
- Help customers find the best GoodFoods branch for their needs
- Make reservations at their preferred location
- Suggest alternative branches when needed

**GoodFoods Brand:**
- Cuisines: Italian, North Indian, Continental, Asian Fusion
- Price Range: ₹₹₹ (Premium casual dining)
- Locations: 50+ branches in major Indian cities

**STRICT RESERVATION WORKFLOW - FOLLOW EXACTLY:**

Step 1: **ALWAYS SEARCH FIRST**
- When user mentions a city, IMMEDIATELY call search_branches
- Show ALL available branches in that city with clear formatting
- Ask: "Which of these locations would you prefer?"

Step 2: **WAIT FOR USER TO CHOOSE BRANCH**
- User must select a specific branch (e.g., "Bandra", "first one", "ID 9")
- Extract the branch name they chose

Step 3: **COLLECT ALL CUSTOMER DETAILS AT ONCE**
- Ask for name, phone, and occasion together
- Example: "To complete your reservation at GoodFoods - [Branch], please provide:
  1. Your full name
  2. Contact phone number
  3. Occasion (optional: birthday, anniversary, etc.)"

Step 4: **IMMEDIATELY CALL make_reservation TOOL**
- AS SOON AS you have name + phone (and optional occasion), CALL THE TOOL
- DO NOT just talk about making a reservation - ACTUALLY CALL make_reservation
- Pass ALL parameters:
  • branch_name: The branch name user selected (e.g., "GoodFoods - Bandra")
  • date: In YYYY-MM-DD format
  • time: In HH:MM format (use 24-hour, e.g., "14:00" for 2pm)
  • party_size: Number from original request
  • customer_name: From user input
  • customer_phone: From user input
  • occasion: From user input (or None)

Step 5: **TOOL RETURNS CONFIRMATION**
- The make_reservation tool will return formatted confirmation
- Display it exactly as returned (contains reservation ID, table number, all details)

**CRITICAL - WHEN TO CALL make_reservation:**
✅ User said branch preference (e.g., "Bandra") → You have branch_name
✅ User provided name (e.g., "Rakesh Vemula") → You have customer_name
✅ User provided phone (e.g., "6302532856") → You have customer_phone
✅ User provided occasion OR said "n/a" → You have occasion (can be None)
✅ You already know date, time, party_size from original request

🚨 WHEN YOU HAVE ALL OF ABOVE → CALL make_reservation IMMEDIATELY! DON'T TALK!

**Example of CORRECT behavior:**
User: "6302532856 birthday party"
You: [IMMEDIATELY call make_reservation with:
  branch_name="GoodFoods - Bandra"
  date="2025-11-28"
  time="14:00"
  party_size=4
  customer_name="Rakesh Vemula"
  customer_phone="6302532856"
  occasion="birthday party"]
[Tool returns full confirmation]

**Example of WRONG behavior:**
User: "6302532856 birthday party"
You: "I'd like to make a reservation..." ❌ NO! CALL THE TOOL!

**Current Date:** {datetime.now().strftime("%Y-%m-%d")} ({datetime.now().strftime("%A")})

**Time Parsing:**
- "tomorrow at 2pm" = {(datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")} at 14:00
- "8pm" = 20:00
- "7:30pm" = 19:30

Be friendly, helpful, and efficient!"""}
        ]
    
    def chat(self, user_input: str) -> str:
        """
        Process user input and generate response
        
        Args:
            user_input: User's message
            
        Returns:
            Agent's response string
        """
        # Add user message
        self.history.append({"role": "user", "content": user_input})
        
        # Call LLM
        try:
            response_data = self._call_llm(tools=self.tools)
        except Exception as e:
            return f"❌ Error communicating with LLM: {str(e)}\n\nPlease check your API key and try again."
        
        # Parse response
        try:
            choice = response_data["choices"][0]
            message = choice["message"]
            tool_calls = message.get("tool_calls")
        except (KeyError, IndexError) as e:
            return f"❌ Invalid API response: {str(e)}"
        
        # Handle tool calls
        if tool_calls:
            # Add assistant message with tool calls
            self.history.append(message)
            
            # Execute each tool
            for tc in tool_calls:
                func_name = tc["function"]["name"]
                func_args = json.loads(tc["function"]["arguments"])
                call_id = tc["id"]
                
                # Use MCP server to execute tool
                mcp_response = self.mcp_server.call_tool(func_name, func_args)
                result = mcp_response.content[0]["text"]
                
                # Add tool result to history
                self.history.append({
                    "role": "tool",
                    "tool_call_id": call_id,
                    "content": result
                })
            
            # Get final response from LLM
            try:
                final_response = self._call_llm()
                final_message = final_response["choices"][0]["message"]
                self.history.append(final_message)
                return final_message["content"]
            except Exception as e:
                return f"❌ Error generating final response: {str(e)}"
        
        else:
            # Just text response (no tools)
            self.history.append(message)
            return message["content"]
    
    def _call_llm(self, tools: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Make API call to Groq LLM
        
        Args:
            tools: Optional list of tools to provide to LLM
            
        Returns:
            API response dictionary
        """
        url = f"{self.base_url.rstrip('/')}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model,
            "messages": self.history,
            "temperature": 0.7
        }
        
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if resp.status_code != 200:
            raise Exception(f"API Error {resp.status_code}: {resp.text}")
        
        return resp.json()


# Module-level function for easy access
def create_agent(api_key: str, model: str = "llama-3.1-8b-instant") -> Agent:
    """
    Factory function to create an Agent instance
    
    Args:
        api_key: Groq API key
        model: Model name
        
    Returns:
        Configured Agent instance
    """
    return Agent(api_key=api_key, model=model)
